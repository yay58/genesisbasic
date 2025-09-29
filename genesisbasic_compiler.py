#!/usr/bin/env python3
"""
GenesisBASIC Compiler - Complete Assembly Generator
Compiles .gb files to Motorola 68000 .asm for Sega Genesis.
On success, prints instructions for ClownAssembler.
"""

import re
import sys
import os
from enum import Enum
import uuid

class TokenType(Enum):
    COMMENT = 'COMMENT'
    DECLARE = 'DECLARE'
    ASSIGN = 'ASSIGN'
    VDP_SET = 'VDP_SET'
    TILE = 'TILE'
    SPRITE = 'SPRITE'
    PALETTE = 'PALETTE'
    READCONTROLLER = 'READCONTROLLER'
    SOUND = 'SOUND'
    SOUNDSTOP = 'SOUNDSTOP'
    MOVE = 'MOVE'
    ADD = 'ADD'
    SUB = 'SUB'
    MUL = 'MUL'
    DIV = 'DIV'
    CMP = 'CMP'
    AND_OP = 'AND_OP'
    OR_OP = 'OR_OP'
    IF = 'IF'
    THEN = 'THEN'
    ELSE = 'ELSE'
    ENDIF = 'ENDIF'
    FOR = 'FOR'
    TO = 'TO'
    STEP = 'STEP'
    NEXT = 'NEXT'
    WHILE = 'WHILE'
    WEND = 'WEND'
    GOTO = 'GOTO'
    GOSUB = 'GOSUB'
    RETURN = 'RETURN'
    POKE = 'POKE'
    PEEK = 'PEEK'
    LABEL = 'LABEL'
    PROC = 'PROC'
    ENDPROC = 'ENDPROC'
    INCLUDE = 'INCLUDE'
    HALT = 'HALT'
    WAITVBLANK = 'WAITVBLANK'
    IDENTIFIER = 'IDENTIFIER'
    NUMBER = 'NUMBER'
    HEX = 'HEX'
    WHITESPACE = 'WHITESPACE'

class GenesisBASICCompiler:
    def __init__(self):
        self.variables = {}  # var: {'type': 'WORD/LONG', 'addr': offset}
        self.labels = set()
        self.asm = []
        self.current_offset = 0xFF0000  # RAM base for variables
        self.errors = []
        self.if_count = 0  # For unique IF labels
        self.line_num = 1
        self.tokenizer = self._build_tokenizer()

    def _build_tokenizer(self):
        patterns = [
            (r'//.*|REM.*', TokenType.COMMENT),
            (r'DIM\s+(\w+)\s+AS\s+(WORD|LONG)(\s*=\s*(\$[\dA-Fa-f]+|\d+))?', TokenType.DECLARE),
            (r'(\w+)\s*=\s*(\$[\dA-Fa-f]+|\d+)', TokenType.ASSIGN),
            (r'VDP\s+SET\s+(\d+),\s*(\$[\dA-Fa-f]+|\d+)', TokenType.VDP_SET),
            (r'TILE\s+(\d+),\s*(\$[\dA-Fa-f]+|\d+),\s*(\d+)', TokenType.TILE),
            (r'SPRITE\s+(\d+),\s*(\$[\dA-Fa-f]+|\d+|\w+),\s*(\$[\dA-Fa-f]+|\d+|\w+),\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+)', TokenType.SPRITE),
            (r'PALETTE\s+(\d+),\s*(.+)', TokenType.PALETTE),
            (r'READCONTROLLER\s+(\d+)', TokenType.READCONTROLLER),
            (r'SOUND\s+(\d+),\s*(\d+),\s*(\d+)', TokenType.SOUND),
            (r'SOUNDSTOP\s+(\d+)', TokenType.SOUNDSTOP),
            (r'MOVE\s+(\w+|\d+|D[0-7]|A[0-6]),\s*(\w+|\d+|D[0-7]|A[0-6])', TokenType.MOVE),
            (r'ADD\s+(\w+),\s*(\$[\dA-Fa-f]+|\d+|\w+)', TokenType.ADD),
            (r'SUB\s+(\w+),\s*(\$[\dA-Fa-f]+|\d+|\w+)', TokenType.SUB),
            (r'MUL\s+(\w+),\s*(\$[\dA-Fa-f]+|\d+|\w+)', TokenType.MUL),
            (r'DIV\s+(\w+),\s*(\$[\dA-Fa-f]+|\d+|\w+)', TokenType.DIV),
            (r'CMP\s+(\w+),\s*(\$[\dA-Fa-f]+|\d+|\w+)', TokenType.CMP),
            (r'IF\s+(\w+)\s+(AND|=|>|<)\s+(\d+|\w+|\$[\dA-Fa-f]+)\s+THEN', TokenType.IF),
            (r'ELSE', TokenType.ELSE),
            (r'ENDIF', TokenType.ENDIF),
            (r'FOR\s+(\w+)\s*=\s*(\d+)\s+TO\s*(\d+)(?:\s+STEP\s+(\d+))?', TokenType.FOR),
            (r'NEXT\s+(\w+)', TokenType.NEXT),
            (r'WHILE\s+(\w+)\s+(=|>|<)\s+(\d+|\w+|\$[\dA-Fa-f]+)', TokenType.WHILE),
            (r'WEND', TokenType.WEND),
            (r'GOTO\s+(\w+)', TokenType.GOTO),
            (r'GOSUB\s+(\w+)', TokenType.GOSUB),
            (r'RETURN', TokenType.RETURN),
            (r'POKE\s+(\$[\dA-Fa-f]+|\d+|\w+),\s*(\$[\dA-Fa-f]+|\d+|\w+)', TokenType.POKE),
            (r'PEEK\s*\((\$[\dA-Fa-f]+|\d+|\w+)\)', TokenType.PEEK),
            (r'(\w+):', TokenType.LABEL),
            (r'PROC\s+(\w+)\s*\((.*?)\)', TokenType.PROC),
            (r'ENDPROC', TokenType.ENDPROC),
            (r'INCLUDE\s+"([^"]+)"', TokenType.INCLUDE),
            (r'HALT', TokenType.HALT),
            (r'WAITVBLANK', TokenType.WAITVBLANK),
            (r'\$[\dA-Fa-f]+', TokenType.HEX),
            (r'\d+', TokenType.NUMBER),
            (r'\w+', TokenType.IDENTIFIER),
            (r'\s+', TokenType.WHITESPACE),
        ]
        regex = '|'.join(f'(?P<{p[1].name}>{p[0]})' for p in patterns)
        return re.compile(regex, re.IGNORECASE | re.MULTILINE)

    def tokenize(self, code):
        tokens = []
        for match in self.tokenizer.finditer(code):
            type_name = match.lastgroup
            value = match.group(type_name)
            if type_name != TokenType.WHITESPACE.name and type_name != TokenType.COMMENT.name:
                tokens.append((TokenType[type_name], value.strip()))
            if '\n' in value:
                self.line_num += value.count('\n')
        return tokens

    def add_error(self, msg):
        self.errors.append(f"Error line {self.line_num}: {msg}")

    def declare_var(self, name, var_type, init=None):
        if name in self.variables:
            self.add_error(f"Variable {name} redeclared")
            return
        offset = self.current_offset
        self.variables[name] = {'type': var_type, 'addr': f'${offset:06X}'.upper()}
        self.current_offset += 2 if var_type == 'WORD' else 4
        if init:
            size = 'w' if var_type == 'WORD' else 'l'
            init_val = f"#{init}" if not init.startswith('$') else init
            self.asm.append(f"    move.{size} {init_val}, {name}")

    def emit_header(self):
        self.asm = [
            "; GenesisBASIC Compiled ROM",
            "    org $000000",
            "    dc.l $00FFFE00      ; Stack pointer",
            "    dc.l rom_header     ; ROM start",
            "    dc.l $00000000      ; Unused",
            "    dc.l Start          ; Reset vector",
            "",
            "rom_header:",
            "    dc.b 'SEGA GENESIS    '  ; Console name",
            "    dc.b '(C) 2025       '   ; Copyright",
            "    dc.b 'GenesisBASIC Demo   '  ; Domestic name",
            "    dc.b 'GenesisBASIC Demo   '  ; Overseas name",
            "    dc.b 'GM 00000000-00'    ; Serial",
            "    dc.w $0000               ; Checksum (post-calculate)",
            "    dc.b 'J               '   ; I/O support",
            "    dc.l rom_start",
            "    dc.l rom_end",
            "    dc.l $00FF0000           ; RAM start",
            "    dc.l $00FFFFFF           ; RAM end",
            "    dc.b $40, $00, $00       ; Subtitles",
            "    dc.b '    '              ; Region",
            "    dc.b $00                 ; ROM type",
            "    dc.w $0000               ; Product number",
            "    dc.b $40                 ; Data area size",
            "    dc.b $00                 ; Reserved",
            "",
            "rom_start:",
            "Start:"
        ]

    def resolve_operand(self, op):
        if op in self.variables:
            return f"({op})"
        if op in ('D0','D1','D2','D3','D4','D5','D6','D7','A0','A1','A2','A3','A4','A5','A6'):
            return op
        if op.startswith('$') or op.isdigit():
            return f"#{op}"
        self.add_error(f"Invalid operand: {op}")
        return op

    def compile(self, code, output_file='output.asm'):
        self.errors = []
        self.variables = {}
        self.labels = set()
        self.current_offset = 0xFF0000
        self.line_num = 1
        tokens = self.tokenize(code)
        
        self.emit_header()
        i = 0
        while i < len(tokens):
            tok_type, value = tokens[i]
            if tok_type == TokenType.DECLARE:
                parts = re.match(r'DIM\s+(\w+)\s+AS\s+(WORD|LONG)(\s*=\s*(\$[\dA-Fa-f]+|\d+))?', value, re.IGNORECASE).groups()
                name, vtype, _, init = parts
                self.declare_var(name, vtype, init)
                i += 1
            elif tok_type == TokenType.VDP_SET:
                reg, val = re.match(r'VDP\s+SET\s+(\d+),\s*(\$[\dA-Fa-f]+|\d+)', value, re.IGNORECASE).groups()
                val_int = int(val, 16) if val.startswith('$') else int(val)
                vdp_addr = 0x8000 | (int(reg) << 8) | (val_int & 0xFF)
                self.asm.append(f"    move.w #{vdp_addr}, $C00004")
                i += 1
            elif tok_type == TokenType.TILE:
                id_, addr, size = re.match(r'TILE\s+(\d+),\s*(\$[\dA-Fa-f]+|\d+),\s*(\d+)', value, re.IGNORECASE).groups()
                addr_int = int(addr, 16) if addr.startswith('$') else int(addr)
                self.asm.append(f"    move.l #{addr_int << 16 | 2}, $C00004  ; Set VRAM write addr")
                self.asm.append(f"    ; TODO: DMA {size} words to VRAM")
                i += 1
            elif tok_type == TokenType.SPRITE:
                parts = re.match(r'SPRITE\s+(\d+),\s*(\$[\dA-Fa-f]+|\d+|\w+),\s*(\$[\dA-Fa-f]+|\d+|\w+),\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+)', value, re.IGNORECASE).groups()
                sid, x, y, tile, pal, hflip, vflip = parts
                sprite_addr = 0xE000 | (int(sid) * 8)
                self.asm.append(f"    move.l #{sprite_addr << 16 | 3}, $C00004  ; Sprite table")
                self.asm.append(f"    move.w {self.resolve_operand(x)}, $C00000  ; Y pos")
                self.asm.append(f"    move.w #{(int(sid) << 8) | (int(pal) << 5) | int(tile)}, $C00000  ; Link/Pal/Tile")
                self.asm.append(f"    move.w {(int(hflip) << 11) | (int(vflip) << 12) | int(self.resolve_operand(x))}, $C00000  ; X pos")
                i += 1
            elif tok_type == TokenType.PALETTE:
                id_, colors = re.match(r'PALETTE\s+(\d+),\s*(.+)', value, re.IGNORECASE).groups()
                colors = [c.strip() for c in colors.split(',')]
                cram_addr = 0xC000 | (int(id_) * 32)
                self.asm.append(f"    move.l #{cram_addr << 16 | 9}, $C00004  ; CRAM write")
                for color in colors[:16]:  # Max 16 colors
                    color_val = int(color, 16) if color.startswith('$') else int(color)
                    self.asm.append(f"    move.w #{color_val}, $C00000")
                i += 1
            elif tok_type == TokenType.READCONTROLLER:
                port = re.match(r'READCONTROLLER\s+(\d+)', value, re.IGNORECASE).group(1)
                self.asm.extend([
                    f"    move.b #$40, $A100{(0x3 if port=='0' else 0x5)}  ; Latch",
                    "    nop",
                    "    nop",
                    f"    move.b $A100{(0x3 if port=='0' else 0x5)}, D0",
                    "    not.b D0  ; Invert bits",
                ])
                i += 1
            elif tok_type == TokenType.SOUND:
                ch, note, vol = re.match(r'SOUND\s+(\d+),\s*(\d+),\s*(\d+)', value, re.IGNORECASE).groups()
                self.asm.extend([
                    f"    move.b #{int(ch)}, $4000  ; YM2612 port A",
                    f"    move.b #{note}, $4001",
                    f"    move.b #{int(ch) + 0x10}, $4000  ; Volume",
                    f"    move.b #{127-int(vol)}, $4001  ; Inverted volume"
                ])
                i += 1
            elif tok_type == TokenType.MOVE:
                src, dst = re.match(r'MOVE\s+(\w+|\d+|D[0-7]|A[0-6]),\s*(\w+|\d+|D[0-7]|A[0-6])', value, re.IGNORECASE).groups()
                src_op = self.resolve_operand(src)
                dst_op = self.resolve_operand(dst)
                size = '.w' if (dst in self.variables and self.variables[dst]['type'] == 'WORD') or dst.startswith('D') else '.l'
                self.asm.append(f"    move{size} {src_op}, {dst_op}")
                i += 1
            elif tok_type == TokenType.ADD:
                dst, src = re.match(r'ADD\s+(\w+),\s*(\$[\dA-Fa-f]+|\d+|\w+)', value, re.IGNORECASE).groups()
                src_op = self.resolve_operand(src)
                self.asm.append(f"    add.w {src_op}, ({dst})")
                i += 1
            elif tok_type == TokenType.SUB:
                dst, src = re.match(r'SUB\s+(\w+),\s*(\$[\dA-Fa-f]+|\d+|\w+)', value, re.IGNORECASE).groups()
                src_op = self.resolve_operand(src)
                self.asm.append(f"    sub.w {src_op}, ({dst})")
                i += 1
            elif tok_type == TokenType.IF:
                var, op, val = re.match(r'IF\s+(\w+)\s+(AND|=|>|<)\s+(\d+|\w+|\$[\dA-Fa-f]+)\s+THEN', value, re.IGNORECASE).groups()
                self.if_count += 1
                label = f"if_{self.if_count}"
                if op == 'AND':
                    self.asm.append(f"    btst #{val}, ({var})")
                    self.asm.append(f"    beq .{label}_skip")
                elif op == '=':
                    self.asm.append(f"    cmp.w {self.resolve_operand(val)}, ({var})")
                    self.asm.append(f"    bne .{label}_skip")
                elif op == '>':
                    self.asm.append(f"    cmp.w {self.resolve_operand(val)}, ({var})")
                    self.asm.append(f"    ble .{label}_skip")
                elif op == '<':
                    self.asm.append(f"    cmp.w {self.resolve_operand(val)}, ({var})")
                    self.asm.append(f"    bge .{label}_skip")
                i += 1
            elif tok_type == TokenType.ENDIF:
                self.asm.append(f".if_{self.if_count}_skip:")
                self.if_count -= 1
                i += 1
            elif tok_type == TokenType.GOTO:
                label = re.match(r'GOTO\s+(\w+)', value, re.IGNORECASE).group(1)
                self.asm.append(f"    bra {label}")
                self.labels.add(label)
                i += 1
            elif tok_type == TokenType.POKE:
                addr, val = re.match(r'POKE\s+(\$[\dA-Fa-f]+|\d+|\w+),\s*(\$[\dA-Fa-f]+|\d+|\w+)', value, re.IGNORECASE).groups()
                addr_op = self.resolve_operand(addr)
                val_op = self.resolve_operand(val)
                self.asm.append(f"    move.w {val_op}, {addr_op}")
                i += 1
            elif tok_type == TokenType.WAITVBLANK:
                self.asm.extend([
                    ".wait_vblank:",
                    "    btst #3, $C00004  ; V-blank flag",
                    "    beq .wait_vblank"
                ])
                i += 1
            elif tok_type == TokenType.LABEL:
                label = value[:-1]
                self.asm.append(f"{label}:")
                self.labels.add(label)
                i += 1
            elif tok_type == TokenType.HALT:
                self.asm.append("Halt: bra Halt")
                i += 1
            else:
                self.add_error(f"Unknown token: {value}")
                i += 1

        # Allocate variables
        self.asm.append("")
        self.asm.append("; Variable allocations")
        for name, info in self.variables.items():
            self.asm.append(f"{name}: ds.{info['type'].lower()} 1")
        self.asm.append("    even")
        self.asm.append("rom_end:")
        self.asm.append("    end")

        asm_code = '\n'.join(self.asm)

        if self.errors:
            print("Compilation errors:")
            for err in self.errors:
                print(err)
            return False, None

        with open(output_file, 'w') as f:
            f.write(asm_code)

        print(f"Successfully generated {output_file}")
        return True, asm_code

    def _print_rom_instructions(self, asm_file):
        print("\n=== Assemble to ROM with ClownAssembler ===")
        print("1. Clone: git clone https://github.com/Clownacy/clownassembler.git")
        print("2. Build: cd clownassembler && make assemblers")
        print("3. Run: ./clownassembler_asm68k -o demo.bin -l demo.lst " + asm_file)
        print("4. Test in emulator (e.g., BlastEm, Gens/GS).")
        print("Note: Use genrom or ihxmerge for checksum if needed.")

def main():
    if len(sys.argv) < 2:
        print("Usage: python genesisbasic_compiler.py <input.gb> [output.asm]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'output.asm'

    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        sys.exit(1)

    with open(input_file, 'r') as f:
        code = f.read()

    compiler = GenesisBASICCompiler()
    success, asm_code = compiler.compile(code, output_file)

    if not success:
        sys.exit(1)

    compiler._print_rom_instructions(output_file)

if __name__ == '__main__':
    main()