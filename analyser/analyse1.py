from androguard.core.analysis.analysis import Analysis
from androguard.core.bytecodes.dvm import Instruction, Instruction12x, Instruction10x, Instruction35c, Instruction31i, \
    Instruction11x, Instruction22x, Instruction32x, Instruction10t, Instruction11n, Instruction20bc, Instruction20t, \
    Instruction21c, Instruction21h, Instruction21s, Instruction21t, Instruction22b, Instruction22c, Instruction22cs, \
    Instruction22s, Instruction22t, Instruction23x, Instruction30t, Instruction31c, Instruction31t, Instruction35mi, \
    Instruction35ms, Instruction3rc, Instruction3rmi, Instruction3rms, Instruction40sc, Instruction41c, Instruction51l, \
    Instruction52c, Instruction5rc

from analyser.analyser import Analyse1MemoryType, PRIMITIVE_TYPES_STR, Analyser, Analyse1StackType
from tools import APKInfos, ExitCode, MethodInfos, MethodKeys, exitError


class Analyse1(Analyser):
    def __init__(self, apkInfos: APKInfos, methodInfos: MethodInfos, analysis: Analysis, verbose: bool):
        # Initialyse memory
        memory: Analyse1MemoryType = [None] * (methodInfos[MethodKeys.LOCALREGISTERCOUNT] + methodInfos[MethodKeys.PARAMETERCOUNT])
        # Smali: Last local register is the "this" (ie: current classname)
        if methodInfos[MethodKeys.LOCALREGISTERCOUNT] > 0 and not methodInfos[MethodKeys.STATIC]:
            memory[methodInfos[MethodKeys.LOCALREGISTERCOUNT] - 1] = methodInfos[MethodKeys.CLASSNAME]
        for index, value in methodInfos[MethodKeys.PARAMS]:
            memory[index] = value

        stack: Analyse1StackType = []
        super().__init__(memory, stack, apkInfos, methodInfos, analysis, verbose)

    # TODO
    def _analyse35c(self, _instruction: Instruction35c) -> None:
        match _instruction.get_name():
            case 'invoke-direct':

                params: list[str] = _instruction.get_output().split(', ')[:-1]
                this: str = params[0]
                params = params[1:]
                paramsCount: int = len(params)

                print(f'This: {this}')
                print(f'Params: {params}')
                print(f'Params count: {paramsCount}')

                # TODO ? Check if 'this' reference is a subclass of the class
                # print(f'{this} register content: {_mem[_registerNameToIndex(this)]}')
                # classAnalysis = _analysis.get_class_analysis(_mem[_registerNameToIndex(this)] + ';')
                # extends: str = classAnalysis.extends
                # extendsAnalysis = _analysis.get_class_analysis(extends)
                # print(f'ClassAnalysis: {classAnalysis}')
                # print(f'Extends: {extends}')
                # print(f'ExtendsAnalysis: {extendsAnalysis}')

                for param in params:
                    register = self._registerNameToIndex(param)
                    if not self._validRegisterNumber(register):
                        self._Error_invalidRegisterNumber(_instruction, register)
                    # TODO Check param type is coherent

                # If the method dosen't return void, push the return value to the stack
                returnType: str = self._returnTypeFromMethodString(_instruction.get_output())
                if returnType != 'V':
                    self._stack.append(returnType)

                exit(1)
            case x:
                exitError(f'Unhandled instruction35c subtype {x}', ExitCode.UNHANDLED_CASE)

    # TODO
    def _analyse21c(self, _instruction: Instruction21c) -> None:
        match _instruction.get_name():
            case 'check-cast':
                register: int = self._registerNameToIndex(self._findOperand(_instruction, 0))
                if not self._validRegisterNumber(register):
                    self._Error_invalidRegisterNumber(_instruction, register)
                if self._mem[register] in PRIMITIVE_TYPES_STR or self._mem[register] is None:
                    exitError(f'Instruction {_instruction} (check-cast) is a primitive value, not reference-bearing', ExitCode.CHECKCAST_AGAINST_PRIMITIVE)
            # TODO
            case x:
                exitError(f'Unhandled instruction21c subtype {x}', ExitCode.UNHANDLED_CASE)

    # DONE
    def _analyse11n(self, _instruction: Instruction11n) -> None:
        register: int = self._registerNameToIndex(self._findOperand(_instruction, 0))
        if not self._validLocalRegisterNumber(register):
            self._Error_invalidRegisterNumber(_instruction, register)
        self._mem[register] = 'I'

    # DONE
    def _analyse31i(self, _instruction: Instruction11x) -> None:
        register: int = self._registerNameToIndex(self._findOperand(_instruction, 0))
        # const-wide/32 write on a pair of registers
        if _instruction.get_name() == 'const-wide/32':
            if not self._validLocalRegisterNumber(register + 1):
                exitError(f'Instruction {_instruction} uses invalid register number pair ({register}, {register + 1})', ExitCode.INVALID_REGISTER_NUMBER)
            self._mem[register] = 'I'
            self._mem[register + 1] = 'I'
        else:
            if not self._validLocalRegisterNumber(register):
                self._Error_invalidRegisterNumber(_instruction, register)
            self._mem[register] = 'I'

    def analyse(self, _currentInstruction: Instruction) -> None:
        """
        Main method that analyse the given instruction by redirecting it to the corresponding method.
        :param _currentInstruction: The instruction to analyse
        """
        if self._verbose:
            self._printInstruction(_currentInstruction)

        match _currentInstruction:
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
                self._useless(_inst10x)

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
                self._unhandled(_inst11x)

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
                self._unhandled(_inst12x)

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
                self._unhandled(_inst21s)

            # Instruction 21t:
            # if-testz vAA, +BBBB
            #   38 -> `if-eqz`
            #   39 -> `if-nez`
            #   3a -> `if-ltz`
            #   3b -> `if-gez`
            #   3c -> `if-gtz`
            #   3d -> `if-lez`
            case Instruction21t() as _inst21t:
                self._unhandled(_inst21t)

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
                self._unhandled(_inst22b)

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
                self._unhandled(_inst22c)

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
                self._unhandled(_inst22s)

            # Instruction22t:
            # if-test vA, vB, +CCCC
            #   32 -> `if-eq`
            #   33 -> `if-ne`
            #   34 -> `if-lt`
            #   35 -> `if-ge`
            #   36 -> `if-gt`
            #   37 -> `if-le`
            case Instruction22t() as _inst22t:
                self._unhandled(_inst22t)

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
