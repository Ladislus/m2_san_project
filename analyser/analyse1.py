from androguard.core.analysis.analysis import Analysis
from androguard.core.bytecodes.dvm import Instruction, Instruction12x, Instruction10x, Instruction35c, Instruction31i, \
    Instruction11x, Instruction22x, Instruction32x, Instruction10t, Instruction11n, Instruction20bc, Instruction20t, \
    Instruction21c, Instruction21h, Instruction21s, Instruction21t, Instruction22b, Instruction22c, Instruction22cs, \
    Instruction22s, Instruction22t, Instruction23x, Instruction30t, Instruction31c, Instruction31t, Instruction35mi, \
    Instruction35ms, Instruction3rc, Instruction3rmi, Instruction3rms, Instruction40sc, Instruction41c, Instruction51l, \
    Instruction52c, Instruction5rc
from tools import APKInfos, ExitCode, MethodInfos, MethodKeys, exitError, PRIMITIVE_TYPES, SMALI_STRING_TYPE, \
    SMALI_INT_TYPE, SMALI_VOID_TYPE, humanTypeToSmaliType, SMALI_BOOLEAN_TYPE
from analyser.analyser import Analyser, Analyse1MemoryContentType, Analyse1StackContentType


class Analyse1(Analyser):
    def __init__(self, apkInfos: APKInfos, methodInfos: MethodInfos, analysis: Analysis, verbose: bool):
        super().__init__({}, {}, apkInfos, methodInfos, analysis, verbose)

    def _initMemoryFirst(self) -> None:
        assert self._current is not None, f'Current instruction is None'
        # Initialyse memory
        memory: Analyse1MemoryContentType = [None] * (
                self._methodInfos[MethodKeys.LOCALREGISTERCOUNT] + self._methodInfos[MethodKeys.PARAMETERCOUNT])
        # Smali: Last local register is the "this" (ie: current classname)
        if self._methodInfos[MethodKeys.LOCALREGISTERCOUNT] > 0 and not self._methodInfos[MethodKeys.STATIC]:
            memory[self._methodInfos[MethodKeys.LOCALREGISTERCOUNT] - 1] = self._methodInfos[MethodKeys.CLASSNAME] + ';'
        # Add parameters type after the local registers
        for index, value in self._methodInfos[MethodKeys.PARAMS]:
            memory[index] = value
        stack: Analyse1StackContentType = []
        self._mem[self._current] = memory
        self._stack[self._current] = stack

    def _setMemory(self, _predecessors: list[Instruction]) -> bool:
        # Memory dosen't matter in case of return-void
        if self._current.get_name() == 'return-void':
            return True

        # First time we enter the method
        if len(self._mem.keys()) == 0:
            self._initMemoryFirst()
            return True
        # First time we analyse this node
        elif self._current not in self._mem.keys():
            # Union des predecesseurs
            memory: Analyse1MemoryContentType or None = None
            stack: Analyse1StackContentType or None = None
            for predecessor in _predecessors:
                if predecessor not in self._mem.keys():
                    continue
                elif memory is None:
                    memory = self._mem[predecessor].copy()
                    stack = self._stack[predecessor].copy()
                else:
                    predecessorMemory: Analyse1MemoryContentType = self._mem[predecessor]
                    predecessorStack: Analyse1StackContentType = self._stack[predecessor]
                    if len(predecessorMemory) != len(memory):
                        exitError(f'Memory size mismatch between {predecessor} and {self._current}', ExitCode.MEMORY_ERROR)
                    if len(stack) != len(predecessorStack):
                        exitError(f'Stack size mismatch between {predecessor} and {self._current}', ExitCode.MEMORY_ERROR)
                    for index, value in enumerate(predecessorMemory):
                        memory[index] = self._compatibleType(memory[index], value)
                    for index, value in enumerate(predecessorStack):
                        stack[index] = self._compatibleType(stack[index], value)
            if memory is None or stack is None:
                exitError(f'No predecessor memory or stack for instruction {self._current}', ExitCode.NO_MEMORY)
            self._mem[self._current] = memory
            self._stack[self._current] = stack
            return True
        # We already analysed this node
        else:
            previousMemory: Analyse1MemoryContentType = self._mem[self._current].copy()
            previousStack: Analyse1StackContentType = self._stack[self._current].copy()
            for predecessor in _predecessors:
                predecessorMemory: Analyse1MemoryContentType = self._mem[predecessor]
                predecessorStack: Analyse1StackContentType = self._stack[predecessor]
                if len(predecessorMemory) != len(self._mem[self._current]):
                    exitError(f'Memory size mismatch between {predecessor} and {self._current}', ExitCode.MEMORY_ERROR)
                if len(self._stack[self._current]) != len(predecessorStack):
                    exitError(f'Stack size mismatch between {predecessor} and {self._current}', ExitCode.MEMORY_ERROR)
                for index, value in enumerate(predecessorMemory):
                    self._putRegisterContent(index, self._compatibleType(self._getRegisterContent(index), value))
                for index, value in enumerate(predecessorStack):
                    self._stack[self._current][index] = self._compatibleType(self._stack[self._current][index], value)
            # Compare new memory
            if previousMemory != self._mem[self._current]:
                return True
            # Compare new stack
            if previousStack != self._stack[self._current]:
                return True
            return False

    # DONE
    def _analyse10x(self, _instruction: Instruction10x) -> None:
        self._lastWasInvokeKindOrFillNewArray = False
        match _instruction.get_name():
            case 'return-void':
                if self._methodInfos[MethodKeys.RETURNTYPE] != SMALI_VOID_TYPE:
                    exitError(f'Instruction \'{type(_instruction).__name__}\' (return-void) is not in a void method',
                              ExitCode.RETURN_VOID_INSIDE_NON_VOID_METHOD)
            case 'nop' as _nop:
                self._useless(_nop)
            case _error:
                exitError(f'Instruction \'{type(_instruction).__name__}\' is not a valid instruction10x',
                          ExitCode.INVALID_INSTRUCTION)

    # Done
    # TODO Comment
    def _analyse11n(self, _instruction: Instruction11n) -> None:
        self._lastWasInvokeKindOrFillNewArray = False
        registerIndex: int = _instruction.A
        if not self._isValidLocalRegisterNumber(registerIndex):
            self._Error_invalidRegisterNumber(_instruction, registerIndex)
        # self._mem[registerIndex] = SMALI_INT_TYPE
        self._putRegisterContent(registerIndex, SMALI_INT_TYPE)

    # TODO
    def _analyse35c(self, _instruction: Instruction35c) -> None:
        self._lastWasInvokeKindOrFillNewArray = True
        match _instruction.get_name():
            case 'invoke-direct' | 'invoke-virtual' | 'invoke-super' | 'invoke-interface':
                # Retrieved the parameters
                providedParameters: list[int] = self._getVariadicProvidedParameters(_instruction)
                # Extract the 'this' register (first one)
                thisRegisterIndex: int = providedParameters.pop(0)
                thisRegisterContent: str = self._getRegisterContent(thisRegisterIndex)
                # Decompose the called method
                calledMethodClass, calledMethodName, calledMethodParameters, calledMethodReturn = self._decomposeInvokedMethod(
                    _instruction)

                # Check if the class is a subclass of the class containing the called method
                if not self._isSubclass(thisRegisterContent, calledMethodClass):
                    exitError(f'Class {thisRegisterContent} is not a subclass of {calledMethodClass}',
                              ExitCode.INVALID_SUBCLASS)

                # Check if the number of paramters is correct
                if len(providedParameters) != len(calledMethodParameters):
                    exitError(
                        f'Method {calledMethodName} requires {len(calledMethodParameters)}, but {len(providedParameters)} given',
                        ExitCode.PARAMETER_COUNT_MISMATCH)

                # Check parameters consistency
                for parameterIndex, parameterRegisterIndex in enumerate(providedParameters):
                    # Check if the register number is valid
                    if not self._isValidRegisterNumber(parameterRegisterIndex):
                        self._Error_invalidRegisterNumber(_instruction, parameterRegisterIndex)
                    # Check if the content of the given register match the parameter type
                    parameterRegisterContent = self._getRegisterContent(parameterRegisterIndex)
                    # Check if the content of the register is a valid subtype of the parameter type
                    self._validateParameterType(parameterRegisterIndex, parameterRegisterContent,
                                                calledMethodParameters[parameterIndex])

                # If the method doesn't return void, push the return value to the stack
                if calledMethodReturn != SMALI_VOID_TYPE:
                    # self._stack.append(calledMethodReturn)
                    self._putStack(calledMethodReturn)
            case 'invoke-static':
                # Retrieved the parameters
                providedParameters: list[int] = self._getVariadicProvidedParameters(_instruction)
                # Decompose the called method
                calledMethodClass, calledMethodName, calledMethodParameters, calledMethodReturn = self._decomposeInvokedMethod(
                    _instruction)

                # Check if the number of paramters is correct
                if len(providedParameters) != len(calledMethodParameters):
                    exitError(
                        f'Method {calledMethodName} requires {len(calledMethodParameters)}, but {len(providedParameters)} given',
                        ExitCode.PARAMETER_COUNT_MISMATCH)

                # Check parameters consistency
                for parameterIndex, parameterRegisterIndex in enumerate(providedParameters):
                    # Check if the register number is valid
                    if not self._isValidRegisterNumber(parameterRegisterIndex):
                        self._Error_invalidRegisterNumber(_instruction, parameterRegisterIndex)
                    # Check if the content of the given register match the parameter type
                    parameterRegisterContent = self._getRegisterContent(parameterRegisterIndex)
                    # Check if the content of the register is a valid subtype of the parameter type
                    self._validateParameterType(parameterRegisterIndex, parameterRegisterContent,
                                                calledMethodParameters[parameterIndex])

                # If the method doesn't return void, push the return value to the stack
                if calledMethodReturn != SMALI_VOID_TYPE:
                    # self._stack.append(calledMethodReturn)
                    self._putStack(calledMethodReturn)
            case 'filled-new-array':
                # Retrieved the parameters
                providedParameters: list[int] = self._getVariadicProvidedParameters(_instruction)
                # Get the array type
                arrayType: str = _instruction.cm.get_type(_instruction.BBBB)
                arrayContentType: str = arrayType[1:]

                for registerIndex in providedParameters:
                    # Check if the register number is valid
                    if not self._isValidRegisterNumber(registerIndex):
                        self._Error_invalidRegisterNumber(_instruction, registerIndex)
                    # Get the content of the current register
                    registerContent: str = self._getRegisterContent(registerIndex)
                    # Check if the content of the register is a valid subtype of the array type
                    self._validateParameterType(registerIndex, registerContent, arrayContentType)
                # Put the result object onto the stack
                # self._stack.append(arrayType)
                self._putStack(arrayType)
            # TODO
            case _error:
                exitError(f'Unhandled instruction35c subtype \'{_error}\'', ExitCode.UNHANDLED_CASE)

    # TODO
    def _analyse21c(self, _instruction: Instruction21c) -> None:
        self._lastWasInvokeKindOrFillNewArray = False
        # Get the destination register index
        registerIndex: int = _instruction.AA
        match _instruction.get_name():
            case 'check-cast':
                # Check that the register is a valid register
                if not self._isValidLocalRegisterNumber(registerIndex):
                    self._Error_invalidRegisterNumber(_instruction, registerIndex)
                # Check if the content of the register is not a primitive type or is initialized
                if self._getRegisterContent(registerIndex) in PRIMITIVE_TYPES or self._getRegisterContent(
                        registerIndex) is None:
                    exitError(
                        f'Instruction \'{type(_instruction).__name__}\' (check-cast) is a primitive value, not reference-bearing',
                        ExitCode.CHECKCAST_AGAINST_PRIMITIVE_OR_NONE)
                # Cast the argument to the given type (raise an error otherwise)
                # self._mem[registerIndex] = _instruction.cm.get_type(_instruction.BBBB)
                self._putRegisterContent(registerIndex, _instruction.cm.get_type(_instruction.BBBB))
            case 'const-string':
                # Check that the register is a valid register
                if not self._isValidLocalRegisterNumber(registerIndex):
                    self._Error_invalidRegisterNumber(_instruction, registerIndex)
                # Put string into the corresponding register
                # self._mem[registerIndex] = SMALI_STRING_TYPE
                self._putRegisterContent(registerIndex, SMALI_STRING_TYPE)
            case 'new-instance' | 'const-class':
                # Get the register index
                registerIndex: int = _instruction.AA
                # Check that the register is a valid register
                if not self._isValidLocalRegisterNumber(registerIndex):
                    self._Error_invalidRegisterNumber(_instruction, registerIndex)
                itemType: str = _instruction.cm.get_type(_instruction.BBBB)
                if _instruction.get_name() == 'new-instance' and self._isArray(itemType):
                    exitError(f'Type provided tp \'new-instance\' instruction is {itemType}, which is an array type',
                              ExitCode.NEW_INSTANCE_AGAINST_ARRAY)
                # self._mem[registerIndex] = itemType
                self._putRegisterContent(registerIndex, itemType)
            case get if get[1:4] == 'get':
                # Get the register index
                registerIndex: int = _instruction.AA
                # Check that the register is a valid register
                if get.endswith('-wide'):
                    if not self._isValidLocalRegisterNumber(registerIndex + 1):
                        self._Error_invalidRegisterNumber(_instruction, registerIndex + 1)
                else:
                    if not self._isValidLocalRegisterNumber(registerIndex):
                        self._Error_invalidRegisterNumber(_instruction, registerIndex)
                _, fieldType, _ = _instruction.cm.get_field(_instruction.BBBB)
                self._putRegisterContent(registerIndex, fieldType)
                if get.endswith('-wide'):
                    self._putRegisterContent(registerIndex + 1, fieldType)
            case get if get[1:4] == 'put':
                registerIndex = _instruction.AA
                if get.endswith('-wide'):
                    if not self._isValidRegisterNumber(registerIndex + 1):
                        self._Error_invalidRegisterNumber(_instruction, registerIndex + 1)
                    if self._getRegisterContent(registerIndex) != self._getRegisterContent(registerIndex + 1):
                        exitError(f'Type provided to \'put-wide\' instruction is {self._getRegisterContent(registerIndex)} and {self._getRegisterContent(registerIndex + 1)}, which are different', ExitCode.INVALID_REGISTER_TYPE)
                else:
                    if not self._isValidRegisterNumber(registerIndex):
                        self._Error_invalidRegisterNumber(_instruction, registerIndex)
                _, fieldType, _ = _instruction.cm.get_field(_instruction.BBBB)
                if self._getRegisterContent(registerIndex) != fieldType:
                    exitError(f'Type provided to \'put\' instruction is {self._getRegisterContent(registerIndex)}, which is not the same as the field type {fieldType}', ExitCode.INVALID_REGISTER_TYPE)
            # TODO
            case _error:
                exitError(f'Unhandled instruction21c subtype \'{_error}\'', ExitCode.UNHANDLED_CASE)

    # Done
    # TODO Comment
    def _analyse31i(self, _instruction: Instruction31i) -> None:
        self._lastWasInvokeKindOrFillNewArray = False
        registerIndex: int = _instruction.AA
        # const-wide/32 write on a pair of registers
        if _instruction.get_name() == 'const-wide/32':
            if not self._isValidLocalRegisterNumber(registerIndex + 1):
                exitError(
                    f'Instruction \'{type(_instruction).__name__}\' uses invalid register number pair ({registerIndex}, {registerIndex + 1})',
                    ExitCode.INVALID_REGISTER_INDEX)
            # self._mem[registerIndex] = SMALI_INT_TYPE
            # self._mem[registerIndex + 1] = SMALI_INT_TYPE
            self._putRegisterContent(registerIndex, SMALI_INT_TYPE)
            self._putRegisterContent(registerIndex + 1, SMALI_INT_TYPE)
        else:
            if not self._isValidLocalRegisterNumber(registerIndex):
                self._Error_invalidRegisterNumber(_instruction, registerIndex)
            # self._mem[registerIndex] = SMALI_INT_TYPE
            self._putRegisterContent(registerIndex, SMALI_INT_TYPE)

    def _analyse21s(self, _instruction: Instruction21s) -> None:
        self._lastWasInvokeKindOrFillNewArray = False
        registerIndex: int = _instruction.AA
        # const-wide/32 write on a pair of registers
        if _instruction.get_name() == 'const-wide/16':
            if not self._isValidLocalRegisterNumber(registerIndex + 1):
                exitError(
                    f'Instruction \'{type(_instruction).__name__}\' uses invalid register number pair ({registerIndex}, {registerIndex + 1})',
                    ExitCode.INVALID_REGISTER_INDEX)
            # self._mem[registerIndex] = SMALI_INT_TYPE
            # self._mem[registerIndex + 1] = SMALI_INT_TYPE
            self._putRegisterContent(registerIndex, SMALI_INT_TYPE)
            self._putRegisterContent(registerIndex + 1, SMALI_INT_TYPE)
        else:
            if not self._isValidLocalRegisterNumber(registerIndex):
                self._Error_invalidRegisterNumber(_instruction, registerIndex)
            # self._mem[registerIndex] = SMALI_INT_TYPE
            self._putRegisterContent(registerIndex, SMALI_INT_TYPE)

    # TODO
    def _analyse11x(self, _instruction: Instruction11x) -> None:
        # Get the register index
        registerIndex: int = _instruction.AA
        match _instruction.get_name():
            case 'move-result-object' | 'move-result':
                # Check if the last instruction was an invoke-kind or fill-new-array
                if not self._lastWasInvokeKindOrFillNewArray:
                    exitError(
                        f'Instruction \'{type(_instruction).__name__}\' is not preceded by an invoke-kind or fill-new-array instruction',
                        ExitCode.MISSING_INVOKE_KIND_OR_FILL_NEW_ARRAY)
                self._lastWasInvokeKindOrFillNewArray = False
                # Check if the register is a valid register (only in local because we write in them)
                if not self._isValidLocalRegisterNumber(registerIndex):
                    self._Error_invalidRegisterNumber(_instruction, registerIndex)
                # If the stack is empty, nothing to move
                if len(self._stack) == 0:
                    exitError(f'The stack is empty', ExitCode.MOVE_RESULT_ON_EMPTY_STACK)
                # TODO Comment
                # itemType: str = self._stack.pop()
                itemType: str = self._popStack()
                match _instruction.get_name():
                    case 'move-result':
                        if itemType not in PRIMITIVE_TYPES:
                            exitError(f'Move result expects a primitive type on the stack, but \'{itemType}\' provided',
                                      ExitCode.MOVE_RESULT_ON_OBJECT_TYPE)
                    case 'move-result-object':
                        if itemType in PRIMITIVE_TYPES:
                            exitError(
                                f'Move result object expects an object type on the stack, but \'{itemType}\' provided',
                                ExitCode.MOVE_RESULT_OBJECT_ON_PRIMITIVE_TYPE)

                # Move the type of the last element on the stack to the given register
                # self._mem[registerIndex] = itemType
                self._putRegisterContent(registerIndex, itemType)
            case 'return-object' | 'return':
                self._lastWasInvokeKindOrFillNewArray = False
                # Check if the register is a valid register (only in local because we write in them)
                if not self._isValidRegisterNumber(registerIndex):
                    self._Error_invalidRegisterNumber(_instruction, registerIndex)
                # returnedItemType: str = self._mem[registerIndex]
                returnedItemType: str = self._getRegisterContent(registerIndex)
                # return-object can't return a primitive type
                if returnedItemType in PRIMITIVE_TYPES and _instruction.get_name() == 'return-object':
                    exitError(
                        f'Instruction \'{type(_instruction).__name__}\' (return-object) can\'t return a primitive type \'{returnedItemType}\'',
                        ExitCode.RETURN_OBJECT_ON_PRIMITIVE_TYPE)
                # return can't return an object type
                elif returnedItemType not in PRIMITIVE_TYPES and _instruction.get_name() == 'return':
                    exitError(
                        f'Instruction \'{type(_instruction).__name__}\' (return) can\'t return a non-primitive type \'{returnedItemType}\'',
                        ExitCode.RETURN_ON_OBJECT_TYPE)
                # Check if the returned type is compatible with the method return type
                if  not self._isSubclass(returnedItemType, self._methodInfos[MethodKeys.RETURNTYPE]):
                    exitError(
                        f'Method \'{self._methodInfos[MethodKeys.NAME]}\' is supposed to return \'{self._methodInfos[MethodKeys.RETURNTYPE]}\', but \'{returnedItemType}\' given',
                        ExitCode.RETURN_TYPE_MISMATCH)
            # TODO
            case _error:
                exitError(f'Unhandled instruction11x subtype {_error}', ExitCode.UNHANDLED_CASE)

    # Done
    def _analyse21t(self, _instruction: Instruction21t) -> None:
        self._lastWasInvokeKindOrFillNewArray = False
        # Get the register index
        registerIndex: int = _instruction.AA
        # Check if the register is a valid register
        if not self._isValidRegisterNumber(registerIndex):
            self._Error_invalidRegisterNumber(_instruction, registerIndex)
        # Get the offset
        offset: int = _instruction.BBBB
        if offset == 0:
            exitError(f'Instruction \'{type(_instruction).__name__}\' can\'t have a 0 offset', ExitCode.INVALID_OFFSET)

    # TODO Comment
    # Done
    def _analyse22t(self, _instruction: Instruction22t) -> None:
        self._lastWasInvokeKindOrFillNewArray = False
        firstRegisterIndex: int = _instruction.A
        secondRegisterIndex: int = _instruction.A
        if not self._isValidRegisterNumber(firstRegisterIndex):
            self._Error_invalidRegisterNumber(_instruction, firstRegisterIndex)
        if not self._isValidRegisterNumber(secondRegisterIndex):
            self._Error_invalidRegisterNumber(_instruction, secondRegisterIndex)
        if self._getRegisterContent(firstRegisterIndex) != self._getRegisterContent(secondRegisterIndex):
            exitError(f'Instruction \'{type(_instruction).__name__}\' can\'t compare different values types',
                      ExitCode.INVALID_REGISTER_TYPE)
        offset: int = _instruction.CCCC
        if offset == 0:
            exitError(f'Instruction \'{type(_instruction).__name__}\' can\'t have a 0 offset', ExitCode.INVALID_OFFSET)

    # TODO Comment
    def _analyse12x(self, _instruction: Instruction12x) -> None:
        self._lastWasInvokeKindOrFillNewArray = False
        _toRegisterIndex: int = _instruction.A
        _fromRegisterIndex: int = _instruction.B
        _fromRegisterContent: str = self._getRegisterContent(_fromRegisterIndex)
        if not self._isValidRegisterNumber(_fromRegisterIndex):
            self._Error_invalidRegisterNumber(_instruction, _fromRegisterIndex)
        if not self._isValidLocalRegisterNumber(_toRegisterIndex):
            self._Error_invalidRegisterNumber(_instruction, _toRegisterIndex)

        match _instruction.get_op_value():
            # Move
            case 0x1:
                if _fromRegisterContent not in PRIMITIVE_TYPES:
                    exitError(f'Instruction \'{type(_instruction).__name__}\' can\'t copy a non-primitive type',
                              ExitCode.INVALID_REGISTER_TYPE)
                # self._mem[_toRegisterIndex] = _fromRegisterContent
                self._putRegisterContent(_toRegisterIndex, _fromRegisterContent)
            # Move-wide
            case 0x4:
                if _fromRegisterContent not in PRIMITIVE_TYPES:
                    exitError(f'Instruction \'{type(_instruction).__name__}\' can\'t copy a non-primitive type',
                              ExitCode.INVALID_REGISTER_TYPE)
                if not self._isValidRegisterNumber(_fromRegisterIndex + 1):
                    self._Error_invalidRegisterNumber(_instruction, _fromRegisterIndex + 1)
                if not self._isValidLocalRegisterNumber(_toRegisterIndex + 1):
                    self._Error_invalidRegisterNumber(_instruction, _toRegisterIndex + 1)
                if _fromRegisterContent != self._getRegisterContent(_fromRegisterIndex + 1):
                    exitError(
                        f'Instruction \'{type(_instruction).__name__}\' source pair types dosen\'t match(\'{_fromRegisterContent}\', {self._getRegisterContent(_fromRegisterIndex + 1)}\')',
                        ExitCode.INVALID_REGISTER_TYPE)
                # self._mem[_toRegisterIndex] = _fromRegisterContent
                # self._mem[_toRegisterIndex + 1] = self._getRegisterContent(_fromRegisterIndex + 1)
                self._putRegisterContent(_toRegisterIndex, _fromRegisterContent)
                self._putRegisterContent(_toRegisterIndex + 1, self._getRegisterContent(_fromRegisterIndex + 1))
            # Move-object
            case 0x7:
                if _fromRegisterContent in PRIMITIVE_TYPES:
                    exitError(f'Instruction \'{type(_instruction).__name__}\' can\'t copy a primitive type',
                              ExitCode.INVALID_REGISTER_TYPE)
                # self._mem[_toRegisterIndex] = _fromRegisterContent
                self._putRegisterContent(_toRegisterIndex, _fromRegisterContent)
            # Unop neg or not
            case op if 0x7b <= op <= 0x80:
                _splittedOp: list[str] = _instruction.get_name().split('-')
                assert len(
                    _splittedOp) == 2, f'Instruction \'{type(_instruction).__name__}\' has an invalid name \'{_instruction.get_name()}\''
                _op, _type = _splittedOp[0], humanTypeToSmaliType(_splittedOp[1])
                # if self._mem[_fromRegisterIndex] != _type:
                if self._getRegisterContent(_fromRegisterIndex) != _type:
                    exitError(
                        f'Instruction \'{type(_instruction).__name__}\' can\'t negate a \'{self._mem[_fromRegisterIndex]}\'',
                        ExitCode.INVALID_REGISTER_TYPE)
                match _op:
                    case 'neg':
                        # self._mem[_toRegisterIndex] = _type
                        self._putRegisterContent(_toRegisterIndex, _type)
                    case 'not':
                        # self._mem[_toRegisterIndex] = SMALI_BOOLEAN_TYPE
                        self._putRegisterContent(_toRegisterIndex, SMALI_BOOLEAN_TYPE)
                    case _error:
                        exitError(f'Unhandled instruction12x subtype \'{_instruction.get_name()}\' (Op: \'{_error}\')',
                                  ExitCode.UNHANDLED_CASE)
            # Unop cast
            case op if 0x81 <= op <= 0x8f:
                _splittedOp: list[str] = _instruction.get_name().split('-to-')
                assert len(
                    _splittedOp) == 2, f'Instruction \'{type(_instruction).__name__}\' has an invalid name \'{_instruction.get_name()}\''
                _fromType, _toType = [humanTypeToSmaliType(x) for x in _splittedOp]
                # if self._mem[_fromRegisterIndex] != _fromType:
                if self._getRegisterContent(_fromRegisterIndex) != _fromType:
                    exitError(
                        f'Instruction \'{type(_instruction).__name__}\' expects a \'{_fromType}\' on register \'{_fromRegisterIndex}\', but \'{self._mem[_fromRegisterIndex]}\' provided',
                        ExitCode.INVALID_REGISTER_TYPE)
                # self._mem[_toRegisterIndex] = _toType
                self._putRegisterContent(_toRegisterIndex, _toType)
            # Binop 2addr
            case op if 0xb0 <= op <= 0xcf:
                opName: str = _instruction.get_name().rstrip('/2addr')
                _splittedOp: list[str] = opName.split('-')
                assert len(
                    _splittedOp) == 2, f'Instruction \'{type(_instruction).__name__}\' has an invalid name \'{_instruction.get_name()}\''
                _op, _type = _splittedOp[0], humanTypeToSmaliType(_splittedOp[1])
                if not self._isValidRegisterNumber(_toRegisterIndex + 1):
                    self._Error_invalidRegisterNumber(_instruction, _toRegisterIndex)
                if not self._isValidRegisterNumber(_fromRegisterIndex + 1):
                    self._Error_invalidRegisterNumber(_instruction, _fromRegisterIndex)
                if _fromRegisterContent != self._getRegisterContent(_fromRegisterIndex + 1):
                    exitError(
                        f'Instruction \'{type(_instruction).__name__}\' expects a couple of {_type}, but (\'{_fromRegisterContent}\', \'{self._getRegisterContent(_fromRegisterIndex + 1)}\') provided', ExitCode.INVALID_REGISTER_TYPE)
                if self._getRegisterContent(_toRegisterIndex) != self._getRegisterContent(_toRegisterIndex + 1):
                    exitError(
                        f'Instruction \'{type(_instruction).__name__}\' expects a couple of {_type}, but (\'{self._getRegisterContent(_toRegisterIndex)}\', \'{self._getRegisterContent(_toRegisterIndex + 1)}\') provided', ExitCode.INVALID_REGISTER_TYPE)
                # self._mem[_toRegisterIndex] = _type
                self._putRegisterContent(_toRegisterIndex, _type)
            case _error:
                exitError(f'Unhandled instruction12x subtype \'{_error}\'', ExitCode.UNHANDLED_CASE)

    # TODO Comment
    # Done
    def _analyse22b(self, _instruction: Instruction22b) -> None:
        self._lastWasInvokeKindOrFillNewArray = False
        _toRegisterIndex: int = _instruction.AA
        _fromRegisterIndex: int = _instruction.BB
        if not self._isValidLocalRegisterNumber(_toRegisterIndex):
            self._Error_invalidRegisterNumber(_instruction, _toRegisterIndex)
        if not self._isValidRegisterNumber(_fromRegisterIndex):
            self._Error_invalidRegisterNumber(_instruction, _fromRegisterIndex)
        # if self._mem[_fromRegisterIndex] != SMALI_INT_TYPE:
        if self._getRegisterContent(_fromRegisterIndex) != SMALI_INT_TYPE:
            exitError(
                f'Instruction \'{type(_instruction).__name__}\' expects a \'{SMALI_INT_TYPE}\' on register \'{_fromRegisterIndex}\', but \'{self._mem[_fromRegisterIndex]}\' provided',
                ExitCode.INVALID_REGISTER_TYPE)
        if _instruction.get_name().startswith('div') and _instruction.CC == 0:
            exitError(f'Instruction \'{type(_instruction).__name__}\' can\'t divide by 0', ExitCode.DIVIDE_BY_ZERO)
        # self._mem[_toRegisterIndex] = SMALI_INT_TYPE
        self._putRegisterContent(_toRegisterIndex, SMALI_INT_TYPE)

    # TODO Comment
    def _analyse22s(self, _instruction: Instruction22s) -> None:
        self._lastWasInvokeKindOrFillNewArray = False
        _toRegisterIndex: int = _instruction.A
        _fromRegisterIndex: int = _instruction.B
        if not self._isValidLocalRegisterNumber(_toRegisterIndex):
            self._Error_invalidRegisterNumber(_instruction, _toRegisterIndex)
        if not self._isValidRegisterNumber(_fromRegisterIndex):
            self._Error_invalidRegisterNumber(_instruction, _fromRegisterIndex)
        # if self._mem[_fromRegisterIndex] != SMALI_INT_TYPE:
        if self._getRegisterContent(_fromRegisterIndex) != SMALI_INT_TYPE:
            exitError(
                f'Instruction \'{type(_instruction).__name__}\' expects a \'{SMALI_INT_TYPE}\' on register \'{_fromRegisterIndex}\', but \'{self._mem[_fromRegisterIndex]}\' provided',
                ExitCode.INVALID_REGISTER_TYPE)
        if _instruction.get_name().startswith('div') and _instruction.CCCC == 0:
            exitError(f'Instruction \'{type(_instruction).__name__}\' can\'t divide by 0', ExitCode.DIVIDE_BY_ZERO)
        # self._mem[_toRegisterIndex] = SMALI_INT_TYPE
        self._putRegisterContent(_toRegisterIndex, SMALI_INT_TYPE)

    def _analyse22c(self, _instruction: Instruction22c) -> None:
        self._lastWasInvokeKindOrFillNewArray = False
        match _instruction.get_op_value():
            # Case IGet
            case _iinstance if 0x52 <= _iinstance <= 0x58:
                toRegisterIndex: int = _instruction.A
                fromRegisterIndex: int = _instruction.B
                classType, fieldType, _ = _instruction.cm.get_field(_instruction.CCCC)
                if not self._isValidLocalRegisterNumber(toRegisterIndex):
                    self._Error_invalidRegisterNumber(_instruction, toRegisterIndex)
                if _instruction.get_name().endswith('-wide'):
                    if not self._isValidLocalRegisterNumber(toRegisterIndex + 1):
                        self._Error_invalidRegisterNumber(_instruction, toRegisterIndex + 1)
                if not self._isValidRegisterNumber(fromRegisterIndex):
                    self._Error_invalidRegisterNumber(_instruction, fromRegisterIndex)
                if not self._isSubclass(self._getRegisterContent(fromRegisterIndex), classType):
                    exitError(f'Instruction \'{type(_instruction).__name__}\' expects a \'{classType}\' on register \'{fromRegisterIndex}\', but \'{self._getRegisterContent(fromRegisterIndex)}\' provided', ExitCode.INVALID_REGISTER_TYPE)
                self._putRegisterContent(toRegisterIndex, fieldType)
                if _instruction.get_name().endswith('-wide'):
                    self._putRegisterContent(toRegisterIndex + 1, fieldType)
            # Case IPut
            case _iinstance if 0x59 <= _iinstance <= 0x5f:
                fromRegisterIndex: int = _instruction.A
                toRegisterIndex: int = _instruction.B
                classType, fieldType, _ = _instruction.cm.get_field(_instruction.CCCC)

                if not self._isValidRegisterNumber(fromRegisterIndex):
                    self._Error_invalidRegisterNumber(_instruction, fromRegisterIndex)
                if _instruction.get_name().endswith('-wide'):
                    if not self._isValidRegisterNumber(fromRegisterIndex + 1):
                        self._Error_invalidRegisterNumber(_instruction, fromRegisterIndex + 1)
                    if self._getRegisterContent(fromRegisterIndex) != self._getRegisterContent(fromRegisterIndex + 1):
                        exitError(f'Instruction \'{type(_instruction).__name__}\' expects a couple of {fieldType}, but (\'{self._getRegisterContent(fromRegisterIndex)}\', \'{self._getRegisterContent(fromRegisterIndex + 1)}\') provided', ExitCode.INVALID_REGISTER_TYPE)
                if not self._isSubclass(self._getRegisterContent(toRegisterIndex), classType):
                    exitError(f'Instruction \'{type(_instruction).__name__}\' expects a \'{classType}\' on register \'{toRegisterIndex}\', but \'{self._getRegisterContent(toRegisterIndex)}\' provided', ExitCode.INVALID_REGISTER_TYPE)
                if self._getRegisterContent(fromRegisterIndex) != fieldType:
                    exitError(f'Instruction \'{type(_instruction).__name__}\' expects a \'{fieldType}\' on register \'{fromRegisterIndex}\', but \'{self._getRegisterContent(fromRegisterIndex)}\' provided', ExitCode.INVALID_REGISTER_TYPE)
            case _error:
                exitError(f'Unhandled instruction22c subtype \'{_error}\'', ExitCode.UNHANDLED_CASE)

    def analyse(self, _instruction: Instruction, **kwargs) -> bool:
        """
        Main method that analyse the given instruction by redirecting it to the corresponding method.
        :param _instruction: The instruction to analyse
        """
        assert 'predecessors' in kwargs
        predecessors: list[Instruction] = kwargs.get('predecessors', [])

        self._current = _instruction

        if self._verbose:
            self._printInstruction(_instruction)

        if not self._setMemory(predecessors):
            return False

        if self._verbose and _instruction.get_name() != 'return-void':
            self._printMemory()

        match _instruction:
            # Instruction 10t:
            # 28 -> `goto +AA`
            case Instruction10t() as _inst10t:
                self._useless(_inst10t)

            # Instruction 10x:
            # 0 -> `nop`
            # 0e -> `return-void`
            # 3e..43 -> X
            # 73 -> X
            # 79..7a -> X
            # e3..f9 -> X
            case Instruction10x() as _inst10x:
                self._analyse10x(_inst10x)

            # Instruction 11n:
            # 12 -> `const/4 vA, #+B`
            case Instruction11n() as _inst11n:
                self._analyse11n(_inst11n)

            # Instruction 11x:
            # 0a -> `move-result vAA`
            # 0b -> `move-result-wide vAA`
            # 0c -> `move-result-object vAA`
            # 0d -> `move-exception vAA`
            # 0f -> `return vAA`
            # 10 -> `return-wide vAA`
            # 11 -> `return-object vAA`
            # 1d -> `monitor-enter vAA`
            # 1e -> `monitor-exit vAA`
            # 27 -> `throw vAA`
            case Instruction11x() as _inst11x:
                self._analyse11x(_inst11x)

            # Instruction 12x:
            # 01 -> `move vA, vB`
            # 04 -> `move-wide vA, vB`
            # 07 -> `move-object vA, vB`
            # unop vA, vB
            #   7b -> `neg-int`
            #   7c -> `not-int`
            #   7d -> `neg-long`
            #   7e -> `not-long`
            #   7f -> `neg-float`
            #   80 -> `neg-double`
            #   81 -> `int-to-long`
            #   82 -> `int-to-float`
            #   83 -> `int-to-double`
            #   84 -> `long-to-int`
            #   85 -> `long-to-float`
            #   86 -> `long-to-double`
            #   87 -> `float-to-int`
            #   88 -> `float-to-long`
            #   89 -> `float-to-double`
            #   8a -> `double-to-int`
            #   8b -> `double-to-long`
            #   8c -> `double-to-float`
            #   8d -> `int-to-byte`
            #   8e -> `int-to-char`
            #   8f -> `int-to-short`
            # binop/2addr vA, vB
            #   b0 -> `add-int/2addr`
            #   b1 -> `sub-int/2addr`
            #   b2 -> `mul-int/2addr`
            #   b3 -> `div-int/2addr`
            #   b4 -> `rem-int/2addr`
            #   b5 -> `and-int/2addr`
            #   b6 -> `or-int/2addr`
            #   b7 -> `xor-int/2addr`
            #   b8 -> `shl-int/2addr`
            #   b9 -> `shr-int/2addr`
            #   ba -> `ushr-int/2addr`
            #   bb -> `add-long/2addr`
            #   bc -> `sub-long/2addr`
            #   bd -> `mul-long/2addr`
            #   be -> `div-long/2addr`
            #   bf -> `rem-long/2addr`
            #   c0 -> `and-long/2addr`
            #   c1 -> `or-long/2addr`
            #   c2 -> `xor-long/2addr`
            #   c3 -> `shl-long/2addr`
            #   c4 -> `shr-long/2addr`
            #   c5 -> `ushr-long/2addr`
            #   c6 -> `add-float/2addr`
            #   c7 -> `sub-float/2addr`
            #   c8 -> `mul-float/2addr`
            #   c9 -> `div-float/2addr`
            #   ca -> `rem-float/2addr`
            #   cb -> `add-double/2addr`
            #   cc -> `sub-double/2addr`
            #   cd -> `mul-double/2addr`
            #   ce -> `div-double/2addr`
            #   cf -> `rem-double/2addr`
            case Instruction12x() as _inst12x:
                self._analyse12x(_inst12x)

            # Instruction 20bc:
            # TODO https://source.android.com/devices/tech/dalvik/instruction-formats?hl=en#format-ids
            case Instruction20bc() as _inst20bc:
                self._unhandled(_inst20bc)

            # Instruction 20t:
            # 29 -> `goto/16 +AAAA`
            case Instruction20t() as _inst20t:
                self._useless(_inst20t)

            # Instruction 21c:
            # 1a -> `const-string vAA, string@BBBB`
            # 1c -> `const-class vAA, type@BBBB`
            # 1f -> `check-cast vAA, type@BBBB`
            # 22 -> `new-instance vAA, type@BBBB`
            # sstaticop vAA, field@BBBB
            #   60 -> `sget`
            #   61 -> `sget-wide`
            #   62 -> `sget-object`
            #   63 -> `sget-boolean`
            #   64 -> `sget-bytet`
            #   65 -> `sget-char`
            #   66 -> `sget-short`
            #   67 -> `sput`
            #   68 -> `sput-wide`
            #   69 -> `sput-object`
            #   6a -> `sput-boolean`
            #   6b -> `sput-byte`
            #   6c -> `sput-char`
            #   6d -> `sput-short`
            # fe -> `const-method-handle vAA, method_handle@BBBB`
            # ff -> `const-method-type vAA, proto@BBBB`
            case Instruction21c() as _inst21c:
                self._analyse21c(_inst21c)

            # Instruction 21h:
            # 19 -> `const-wide/high16 vAA, #+BBBB000000000000
            # 15 -> `const/high16 vAA, #+BBBB0000
            case Instruction21h() as _inst21h:
                self._unhandled(_inst21h)

            # Instruction 21s:
            # 13 -> `const/16 vAA, #+BBBB
            # 16 -> `const-wide/16 vAA, #+BBBB
            case Instruction21s() as _inst21s:
                self._analyse21s(_inst21s)

            # Instruction 21t:
            # if-testz vAA, +BBBB
            #   38 -> `if-eqz`
            #   39 -> `if-nez`
            #   3a -> `if-ltz`
            #   3b -> `if-gez`
            #   3c -> `if-gtz`
            #   3d -> `if-lez`
            case Instruction21t() as _inst21t:
                self._analyse21t(_inst21t)

            # Instruction 22b:
            # binop/lit8 vAA, vBB, #+CC
            #   d8 -> `add-int/lit8`
            #   d9 -> `rsub-int/lit8`
            #   da -> `mul-int/lit8`
            #   db -> `div-int/lit8`
            #   dc -> `rem-int/lit8`
            #   dd -> `and-int/lit8`
            #   de -> `or-int/lit8`
            #   df -> `xor-int/lit8`
            #   e0 -> `shl-int/lit8`
            #   e1 -> `shr-int/lit8`
            #   e2 -> `ushr-int/lit8`
            case Instruction22b() as _inst22b:
                self._analyse22b(_inst22b)

            # Instruction 22c:
            # 20 -> `instance-of vA, vB, type@CCCC`
            # 23 -> `new-array vA, vB, type@CCCC`
            # iinstanceop vA, vB, field@CCCC
            #   52 -> `iget`
            #   53 -> `iget-wide`
            #   54 -> `iget-object`
            #   55 -> `iget-boolean`
            #   56 -> `iget-byte`
            #   57 -> `iget-char`
            #   58 -> `iget-short`
            #   59 -> `iput`
            #   5a -> `iput-wide`
            #   5b -> `iput-object`
            #   5c -> `iput-boolean`
            #   5d -> `iput-byte`
            #   5e -> `iput-char`
            #   5f -> `iput-short`
            case Instruction22c() as _inst22c:
                self._analyse22c(_inst22c)

            # Instruction 22cs:
            # TODO https://source.android.com/devices/tech/dalvik/instruction-formats?hl=en#format-ids
            case Instruction22cs() as _inst22cs:
                self._unhandled(_inst22cs)

            # Instruction 22s:
            # binop/lit16 vA, vB, #+CCCC
            #   d0 -> `add-int/lit16`
            #   d1 -> `rsub-int (reverse subtract)`
            #   d2 -> `mul-int/lit16`
            #   d3 -> `div-int/lit16`
            #   d4 -> `rem-int/lit16`
            #   d5 -> `and-int/lit16`
            #   d6 -> `or-int/lit16`
            #   d7 -> `xor-int/lit16`
            case Instruction22s() as _inst22s:
                self._analyse22s(_inst22s)

            # Instruction22t:
            # if-test vA, vB, +CCCC
            #   32 -> `if-eq`
            #   33 -> `if-ne`
            #   34 -> `if-lt`
            #   35 -> `if-ge`
            #   36 -> `if-gt`
            #   37 -> `if-le`
            case Instruction22t() as _inst22t:
                self._analyse22t(_inst22t)

            # Instruction 22x:
            # 02  -> `move/from16 vAA, vBBBB`
            # 05  -> `move-wide/from16 vAA, vBBBB`
            # 08  -> `move-object/from16 vAA, vBBBB`
            case Instruction22x() as _inst22x:
                self._unhandled(_inst22x)

            # Instruction 23x:
            # cmpkind vAA, vBB, vCC
            #   2d -> `cmpl-float (lt bias)`
            #   2e -> `cmpg-float (gt bias)`
            #   2f -> `cmpl-double (lt bias)`
            #   30 -> `cmpg-double (gt bias)`
            #   31 -> `cmp-long`
            # arrayop vAA, vBB, vCC
            #   44 -> `aget`
            #   45 -> `aget-wide`
            #   46 -> `aget-object`
            #   47 -> `aget-boolean`
            #   48 -> `aget-byte`
            #   49 -> `aget-char`
            #   4a -> `aget-short`
            #   4b -> `aput`
            #   4c -> `aput-wide`
            #   4d -> `aput-object`
            #   4e -> `aput-boolean`
            #   4f -> `aput-byte`
            #   50 -> `aput-char`
            #   51 -> `aput-short`
            # binop vAA, vBB, vCC
            #   90 -> `add-int`
            #   91 -> `sub-int`
            #   92 -> `mul-int`
            #   93 -> `div-int`
            #   94 -> `rem-int`
            #   95 -> `and-int`
            #   96 -> `or-int`
            #   97 -> `xor-int`
            #   98 -> `shl-int`
            #   99 -> `shr-int`
            #   9a -> `ushr-int`
            #   9b -> `add-long`
            #   9c -> `sub-long`
            #   9d -> `mul-long`
            #   9e -> `div-long`
            #   9f -> `rem-long`
            #   a0 -> `and-long`
            #   a1 -> `or-long`
            #   a2 -> `xor-long`
            #   a3 -> `shl-long`
            #   a4 -> `shr-long`
            #   a5 -> `ushr-long`
            #   a6 -> `add-float`
            #   a7 -> `sub-float`
            #   a8 -> `mul-float`
            #   a9 -> `div-float`
            #   aa -> `rem-float`
            #   ab -> `add-double`
            #   ac -> `sub-double`
            #   ad -> `mul-double`
            #   ae -> `div-double`
            #   af -> `rem-double`
            case Instruction23x() as _inst23x:
                self._unhandled(_inst23x)

            # Instruction 30t
            # 2a  -> `goto/32 +AAAAAAAA`
            case Instruction30t() as _inst30t:
                self._useless(_inst30t)

            # Instruction 31c:
            # 1b -> `const-string/jumbo vAA, string@BBBBBBBB`
            case Instruction31c() as _inst31c:
                self._unhandled(_inst31c)

            # Instruction31i:
            # 14 -> `const vAA, #+BBBBBBBB`
            # 17 -> `const-wide/32 vAA, #+BBBBBBBB`
            case Instruction31i() as _inst31i:
                self._analyse31i(_inst31i)

            # Instruction31t:
            # 26 -> `fill-array-data vAA, +BBBBBBBB (with supplemental data as specified below in "fill-array-data-payload Format")`
            # 2b -> `packed-switch vAA, +BBBBBBBB (with supplemental data as specified below in "packed-switch-payload Format")`
            # 2c -> `sparse-switch vAA, +BBBBBBBB (with supplemental data as specified below in "sparse-switch-payload Format")`
            case Instruction31t() as _inst31t:
                self._unhandled(_inst31t)

            # Instruction32x:
            # 03 -> `move/16 vAAAA, vBBBB`
            # 06 -> `move-wide/16 vAAAA, vBBBB`
            # 09 -> `move-object/16 vAAAA, vBBBB`
            case Instruction32x() as _inst32x:
                self._unhandled(_inst32x)

            # Instruction35c:
            # 24 -> `filled-new-array {vC, vD, vE, vF, vG}, type@BBBB`
            # invoke-kind {vC, vD, vE, vF, vG}, meth@BBBB
            #   6e -> `invoke-virtual`
            #   6f -> `invoke-super`
            #   70 -> `invoke-direct`
            #   71 -> `invoke-static`
            #   72 -> `invoke-interface`
            # fc -> `invoke-custom {vC, vD, vE, vF, vG}, call_site@BBBB`
            case Instruction35c() as _inst35c:
                self._analyse35c(_inst35c)

            # Instruction35mi:
            # TODO https://source.android.com/devices/tech/dalvik/instruction-formats?hl=en#format-ids
            case Instruction35mi() as _inst35mi:
                self._unhandled(_inst35mi)

            # Instruction35ms:
            # TODO https://source.android.com/devices/tech/dalvik/instruction-formats?hl=en#format-ids
            case Instruction35ms() as _inst35ms:
                self._unhandled(_inst35ms)

            # Instruction3rc:
            # 25 -> `filled-new-array/range {vCCCC .. vNNNN}, type@BBBB`
            # invoke-kind/range {vCCCC .. vNNNN}, meth@BBBB
            #   74 -> invoke-virtual/range
            #   75 -> invoke-super/range
            #   76 -> invoke-direct/range
            #   77 -> invoke-static/range
            #   78 -> invoke-interface/range
            # fd -> `invoke-custom/range {vCCCC .. vNNNN}, call_site@BBBB`
            case Instruction3rc() as _inst3rc:
                self._unhandled(_inst3rc)

            # Instruction3rmi:
            # TODO https://source.android.com/devices/tech/dalvik/instruction-formats?hl=en#format-ids
            case Instruction3rmi() as _inst3rmi:
                self._unhandled(_inst3rmi)

            # Instruction3rms:
            # TODO https://source.android.com/devices/tech/dalvik/instruction-formats?hl=en#format-ids
            case Instruction3rms() as _inst3rms:
                self._unhandled(_inst3rms)

            # Instruction40sc:
            # TODO http://www.dre.vanderbilt.edu/~schmidt/android/android-4.0/dalvik/docs/instruction-formats.html
            case Instruction40sc() as _inst40sc:
                self._unhandled(_inst40sc)

            # Instruction41c:
            # TODO http://www.dre.vanderbilt.edu/~schmidt/android/android-4.0/dalvik/docs/instruction-formats.html
            case Instruction41c() as _inst41c:
                self._unhandled(_inst41c)

            # FIXME Can't find import
            # Instruction45cc:
            # fa -> `invoke-polymorphic {vC, vD, vE, vF, vG}, meth@BBBB, proto@HHHH`
            # case Instruction45cc() as _inst45cc:
            #     self._unhandled(_inst45cc)

            # FIXME Can't find import
            # Instruction4rcc:
            # fb -> `invoke-polymorphic/range {vCCCC .. vNNNN}, meth@BBBB, proto@HHHH`
            # case Instruction4rcc() as _inst4rcc:
            #     self._unhandled(_inst4rcc)

            # Instruction51l:
            # 18 -> `const-wide vAA, #+BBBBBBBBBBBBBBBB`
            case Instruction51l() as _inst51l:
                self._unhandled(_inst51l)

            # Instruction52c:
            # TODO http://www.dre.vanderbilt.edu/~schmidt/android/android-4.0/dalvik/docs/instruction-formats.html
            case Instruction52c() as _inst52c:
                self._unhandled(_inst52c)

            # Instruction5rc:
            # TODO http://www.dre.vanderbilt.edu/~schmidt/android/android-4.0/dalvik/docs/instruction-formats.html
            case Instruction5rc() as _inst5rc:
                self._unhandled(_inst5rc)

            # Unknwon instruction
            case _ as _instruction:
                self._unhandled(_instruction)

        return True
