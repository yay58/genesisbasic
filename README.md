GenesisBASIC Compiler

<img width="390" height="264" alt="image" src="https://github.com/user-attachments/assets/d382f765-3a82-4770-85f3-f81afaddf622" />

A modern compiler for creating Sega Genesis / Mega Drive games using a BASIC-inspired language.

The GenesisBASIC Compiler transforms high-level GenesisBASIC code into Motorola 68000 assembly (.asm) for the Sega Genesis. This JavaScript-based compiler runs in browsers or Node.js, generating ROMs that can be assembled with ClownAssembler and tested in emulators like BlastEm or Gens/GS. It’s designed for retro game developers, hobbyists, and enthusiasts looking to create 16-bit games with a simple, beginner-friendly syntax.



Table of Contents





Features



System Requirements



Installation



Usage





Browser Usage



Node.js Usage



GenesisBASIC Language



Example Program



Assembling the ROM



Screenshots



Contributing



License



Acknowledgments



Features





Cross-Platform: Runs in modern browsers (Chrome, Firefox) or Node.js environments.



Simple Syntax: GenesisBASIC uses a BASIC-inspired language for easy game development.



Full VDP Support: Configure the Sega Genesis Video Display Processor with VDP SET, SPRITE, TILE, and PALETTE commands.



Controller Input: Read 3-button controllers with READCONTROLLER.



Sound Support: Play FM sounds via the YM2612 chip with the SOUND command.



Variable Management: Declare WORD and LONG variables with DIM and manipulate with MOVE, ADD, SUB.



Control Flow: Supports IF, GOTO, and HALT for program logic.



Graphics: Includes 8x8 tile data (white square) and 4x8 font for digits 0-9.



Output: Generates downloadable .asm files via the browser’s Blob API or file writes in Node.js.



Error Handling: Reports syntax errors with line numbers for debugging.





System Requirements







Component



Requirement





Environment



Modern browser (Chrome, Firefox) or Node.js v16+





Assembler



ClownAssembler (for .asm to .bin)





Emulator



BlastEm, Gens/GS, or Kega Fusion





Tools



ucon64 or genrom (for ROM checksum)





OS



Windows, macOS, Linux



Installation





Clone the Repository:

git clone https://github.com/yourusername/genesisbasic-compiler.git
cd genesisbasic-compiler



Install ClownAssembler:

git clone https://github.com/Clownacy/clownassembler.git
cd clownassembler
make assemblers



Install Node.js (Optional):





Download and install Node.js from nodejs.org if using the Node.js version.



ROM Fixer (Optional):





Install ucon64 or genrom for checksum correction:

sudo apt-get install ucon64  # On Ubuntu/Debian



Usage

Browser Usage





Save genesisbasic_compiler.js to your project directory.



Open Chrome DevTools (F12) and go to the Console tab.



Copy and paste the entire genesisbasic_compiler.js code.



The embedded example code will compile and trigger a download of output.asm.



Node.js Usage





Install Node.js dependencies (if writing to disk):

npm install fs



Modify the script to enable file output:

const fs = require('fs');
compiler.compile(exampleCode, 'output.asm').then(result => {
    if (result.success) {
        fs.writeFileSync('output.asm', result.asm);
    }
});



Run the script:

node genesisbasic_compiler.js



GenesisBASIC Language

GenesisBASIC is a simplified language for Sega Genesis development. Key commands include:





DIM: Declare variables (WORD or LONG).

DIM x AS WORD = 160



VDP SET: Configure VDP registers.

VDP SET 0, $40



SPRITE: Define sprite attributes (ID, x, y, tile, palette, hflip, vflip).

SPRITE 0, x, y, 0, 0, 0, 0



TILE: Load tile data to VRAM.

TILE 0, $2000, 32



PALETTE: Set color palette.

PALETTE 0, $EEE, $000, $0EE



READCONTROLLER: Read controller input.

READCONTROLLER 0



SOUND: Play FM sound (channel, note, volume).

SOUND 0, 60, 100



MOVE/ADD/SUB: Manipulate variables.

MOVE buttons, D0
ADD score, 10



IF/ENDIF: Conditional branching.

IF buttons AND 1 THEN
    SUB y, 2
ENDIF



POKE: Write to VDP memory.

POKE $4000, score



WAITVBLANK: Sync with vertical blank.

WAITVBLANK



GOTO/HALT: Control flow.

GOTO MainLoop
HALT



Example Program

The following program moves a white square sprite with the D-pad, plays a sound on the A button, and displays a score (0-99) at the top-left.

REM GenesisBASIC: Sprite Mover with Sound
DIM x AS WORD = 160
DIM y AS WORD = 120
DIM buttons AS WORD
DIM score AS WORD = 0
VDP SET 0, $40
VDP SET 1, $14
VDP SET 5, $E
VDP SET 11, $10
TILE 0, $2000, 32
SPRITE 0, x, y, 0, 0, 0, 0
PALETTE 0, $EEE, $000, $0EE, $EE0, $0E0, $E00, $000, $EEE, $888, $CCC, $EEE, $EEE, $EEE, $EEE, $EEE, $EEE
MainLoop:
  READCONTROLLER 0
  MOVE buttons, D0
  IF buttons AND 1 THEN
    SUB y, 2
    IF y < 0 THEN MOVE y, 0 ENDIF
  ENDIF
  IF buttons AND 2 THEN
    ADD y, 2
    IF y > 200 THEN MOVE y, 200 ENDIF
  ENDIF
  IF buttons AND 4 THEN
    SUB x, 2
    IF x < 0 THEN MOVE x, 0 ENDIF
  ENDIF
  IF buttons AND 8 THEN
    ADD x, 2
    IF x > 300 THEN MOVE x, 300 ENDIF
  ENDIF
  IF buttons AND 64 THEN
    SOUND 0, 60, 100
    ADD score, 10
  ENDIF
  SPRITE 0, x, y, 0, 0, 0, 0
  POKE $4000, score
  WAITVBLANK
  GOTO MainLoop
HALT

Run this in the compiler to generate output.asm.



Assembling the ROM





Compile the Program: Use the JavaScript compiler to generate output.asm.



Assemble with ClownAssembler:

./clownassembler_asm68k /O demo.bin /L demo.lst output.asm



Fix ROM Checksum:

ucon64 --genfix demo.bin



Test in Emulator: Load demo.bin in BlastEm or Gens/GS.





Controls: D-pad moves the sprite, A button plays a sound and increments the score.



Output: A white 8x8 sprite moves, with the score displayed as two digits at the top-left.





Screenshots







Description



Image





Compiler in Browser Console









ROM Running in BlastEm









Generated Assembly Code







Contributing

Contributions are welcome! To contribute:





Fork the repository.



Create a feature branch: git checkout -b feature/awesome-feature



Commit changes: git commit -m 'Add awesome feature'



Push to the branch: git push origin feature/awesome-feature



Open a pull request.

Please include tests and update documentation for new features.



License

This project is licensed under the MIT License. See LICENSE for details.



Acknowledgments





Clownacy for ClownAssembler.



BlastEm and Gens/GS teams for excellent emulators.



Sega Genesis Dev Community for documentation and inspiration.
