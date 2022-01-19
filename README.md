# Projet SAN

## Membres du groupe
 - Corentin HERVOCHON (2171782)
 - Tom RIBARDIERE (2171029)
 - Ladislas WALCAK (2174867)

## Lancement

### Requirements
 - Python3.10
 - Packages dans le fichier requirements.txt (`pip install -r requirements.txt`)

### Exécution
Pour afficher l'aide, utilisez `python3 main.py --help` ou `python3 main.py -h`
```console
usage: main.py [-h] [-i FILE] [-v] APKFile Class {1,2,3}

positional arguments:
  APKFile               Path to the APK file to analyse
  Class                 Name of the class to analyse
  {1,2,3}               Type of analyse

options:
  -h, --help            show this help message and exit
  -i FILE, --input FILE
                        Path to the input file (Analyse 3)
  -v, --verbose         Verbose mode
```
L'option [-I] [--input] n'est pas disponible. L'analyse 3 s'exécute de la même manière que l'analyse 1 et 2.

Lors d'une erreur, le programme s'arrête et affiche l'erreur dans STDERR.  

**Attention**: 
Avec l'option [-v] ou [--verbose], il se peut que l'erreur ne soit pas le dernier message affiché (problème de buffer des prints).  
Pour vérifier qu'une erreur est bien parvenue, regardez le code de sortie.

## APKs
Toutes les APKs contenu dans le dossier APK (à la racine du dossier) peuvent être analysées avec les 3 analyses.
Pour tester les erreurs, référez-vous au sous-dossier correspondant au nom de l'analyse.

 - Analyse 1:
   - APKs\Analyse1\Analyse1PredecessorsMergeError.apk: Erreur lors de la fusion des mémoires et stacks des prédécesseurs
   - APKs\Analyse1\Analyse1WrongFieldType.apk: Tentavide de `iput` sur un champs du mauvais type
   - APKs\Analyse1\Analyse1WrongReturnType.apk: L'objet retourné par la méthode n'est pas du bon type
   - APKs\Analyse1\Analyse1WrongRegisterIndex.apk: Tentative d'utilisation d'un register nom défini
 - Analyse 2: 
   - APKs\Analyse\Analyse2NoInit.apk: Tentative d'utilisation d'un objet non initialisé
  
Il existe d'autres erreurs qui peuvent être trouvées par l'outil, mais nous n'avons pas d'APK permettant de les testées


## Instructions implémentées
| Instruction         | OP Code - Nom                                                | Implémenté |
| :-----------------: |:-------------------------------------------------------------|:----------:|
| Instruction 10t     | 28 -> `goto +AA`                                             |     X      |
| Instruction 10x     | 0 -> `nop`                                                   |     X      |
|                     | 0e -> `return-void`                                          |     X      |
| Instruction 11n     | 12 -> `const/4 vA, #v+B`                                     |     X      |
| Instruction 11x     | 0a -> `move-result vAA`                                      |     X      |
|                     | 0b -> `move-result-wide vAA`                                 |            |
|                     | 0c -> `move-result-object vAA`                               |     X      |
|                     | 0d -> `move-exception vAA`                                   |            |
|                     | 0f -> `return vAA`                                           |     X      |
|                     | 10 -> `return-wide vAA`                                      |            |
|                     | 11 -> `return-object vAA`                                    |     X      |
|                     | 1d -> `monitor-enter vAA`                                    |            |
|                     | 1e -> `monitor-exit vAA`                                     |            |
|                     | 27 -> `throw vAA`                                            |            |
| Instruction 12x     | 01 -> `move vA, Vb`                                          |     X      |
|                     | 04 -> `move-wide vA, Vb`                                     |     X      |
|                     | 07 -> `move-object vA, Vb`                                   |     X      |
|                     | 7b..8f -> `unop vA, vb`                                      |     X      |
|                     | b0..cf -> `binop/addr vA, Vb`                                |     X      |
| Instruction 20t     | 29 -> `goto/16 +AAAA`                                        |     X      |
| Instruction 21c     | 1a -> `const-string vAA, string@BBBB`                        |     X      |
|                     | 1c -> `const-class vAA, type@BBBB`                           |     X      |
|                     | 1f -> `check-cast vAA, type@BBBB `                           |     X      |
|                     | 22 -> `new-instance vAA, type@BBBB`                          |     X      |
|                     | 60..6d -> `sstaticop vAA, field@BBBB`                        |     X      |
|                     | fe -> `const-method-handle vAA, method_handle@BBBB`          |            |
|                     | ff -> `const-method-handle vAA, proto@BBBB`                  |            |
| Instruction 21h     | 19 -> `const-wide/high16 vAA, #+BBBB000000000000`            |            |
|                     | 15 -> `const/high16 vAA, #+BBBB0000 `                        |            |
| Instruction 21s     | 13 -> `const/16 vAA, #+BBBB`                                 |     X      |
|                     | 16 -> `const-wide vAA, #+BBBB `                              |     X      |
| Instruction 21t     | 38..3d -> `if-testz vAA, +BBBB`                              |     X      |
| Instruction 22b     | d8..e2 -> `binop/lit8 vAA, vBB, #+CC`                        |     X      |
| Instruction 22c     | 20 -> `instance-of vA, vB, type@CCCC`                        |            |
|                     | 23 -> `new-array vA, vB, type@CCCC`                          |            |
|                     | 52..5f -> `iinstanceop vA, vB, field@CCCC`                   |     X      |
| Instruction 22s     | d0..d7 -> `binop/lit16 vA, vB, #+CCCC`                       |     X      |
| Instruction 22t     | 32..37 -> `if-test vA, vB, +CCCC`                            |     X      |
| Instruction 22x     | 02 -> `move/from16 vAA, vBBBB`                               |            |
|                     | 05 -> `move-wide/from16 vAA, vBBBB`                          |            |
|                     | 08 -> `move-object/from16 vAA, vBBBB`                        |            |
| Instruction 23x     | 2d..31 -> `cmpkind vAA, vBB, vCC`                            |            |
|                     | 44..51 -> `arrayop vAA, vBB, vCC`                            |            |
|                     | 90..af -> `binop vAA, vBB, vCC`                              |            |
| Instruction 30t     | 2a -> `goto/32 +AAAAAAAA`                                    |     X      |
| Instruction 31c     | 1b -> `const-string/jumbo vAA, string@BBBBBBBB`              |            |
| Instruction 31i     | 14 -> `const vAA, #+BBBBBBBB`                                |     X      |
|                     | 17 -> `const-wide/32 vAA, #+BBBBBBBB`                        |     X      |
| Instruction 31t     | 26 -> `fill-array-data vAA, +BBBBBBBB`                       |            |
|                     | 2b -> `packed-switch vAA, +BBBBBBBB`                         |            |
|                     | 2c -> `sparse-switch vAA, +BBBBBBBB`                         |            |
| Instruction 32x     | 03 -> `move/16 vAAAA, vBBBB`                                 |            |
|                     | 06 -> `move-wide/16 vAAAA, vBBBB`                            |            |
|                     | 09 -> `move-object/16 vAAAA, vBBBB`                          |            |
| Instruction 35c     | 24 -> `filled-new-array {vC, vD, vE, vF, vG}, type@BBBB`     |     X      |
|                     | 6e..72 -> `invoke-kind {vC, vD, vE, vF, vG}, meth@BBBB`      |     X      |
|                     | fc -> `invoke-custom {vC, vD, vE, vF, vG}, call_site@BBBB`   |            |
| Instruction 3rc     | 25 -> `filled-new-array/range {vCCCC .. vNNNN}, type@BBBB`   |            |
|                     | 74..78 -> `invoke-kind/range {vCCCC .. vNNNN}, meth@BBBB`    |            |
|                     | fd -> `invoke-custom/range {vCCCC .. vNNNN}, call_site@BBBB` |            |
| Instruction 51l     | 18 ->  `const-wide vAA, #+BBBBBBBBBBBBBBBB`                  |            |

## Liens
 - [Documentation Dalvik](https://source.android.com/devices/tech/dalvik/dalvik-bytecode)
 - [Documentation Androguard](https://androguard.readthedocs.org/)
 - [Exemples d'instruction Dalvik](http://pallergabor.uw.hu/androidblog/dalvik_opcodes.html)
 - [Wiki Smali](https://github.com/JesusFreke/smali/wiki)