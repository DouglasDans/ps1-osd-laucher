"""
ps1_font.py — helper para usar o sprite sheet da fonte PS1 no pygame.

Uso básico:
    import pygame
    from ps1_font import PS1Font

    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    font = PS1Font('ps1_font_sheet.png', 'ps1_font.json')

    font.render(screen, "HELLO WORLD", x=50, y=100)
    font.render(screen, "hello world", x=50, y=160, color=(200, 200, 100))
    font.render(screen, "12345 +-=?!", x=50, y=220, scale=0.5)
"""

import pygame
import json

class PS1Font:
    def __init__(self, sheet_path: str, json_path: str):
        """
        sheet_path : caminho para ps1_font_sheet.png
        json_path  : caminho para ps1_font.json
        """
        # Carrega o sheet como surface com alpha
        raw = pygame.image.load(sheet_path).convert_alpha()

        # Lê metadados
        with open(json_path) as f:
            meta = json.load(f)

        self.glyphs: dict[str, tuple] = {}  # char → Surface recortada
        self.glyph_rects = meta['glyphs']   # char → [x, y, w, h]

        # Pré-recorta cada glifo em sua própria Surface (branco puro)
        for char, (x, y, w, h) in self.glyph_rects.items():
            sub = raw.subsurface((x, y, w, h)).copy()
            self.glyphs[char] = sub

        self.line_height: int = meta['cell_h']
        self.kerning: int = 7   # pixels extras entre chars

    # ── render ────────────────────────────────────────────────────────────────
    def render(
        self,
        surface: pygame.Surface,
        text: str,
        x: int,
        y: int,
        color: tuple[int, int, int] = (255, 255, 255),
        scale: float = 1.0,
        space_width: int = 18,
    ) -> int:
        """
        Desenha `text` em `surface` a partir de (x, y).
        Retorna a coordenada x final (útil pra encadear chamadas).

        color       : cor RGB dos glifos (tint sobre branco)
        scale       : fator de escala (0.5 = metade do tamanho)
        space_width : largura em px do caractere espaço
        """
        cx = x
        for char in text:
            if char == ' ':
                cx += int(space_width * scale)
                continue
            if char not in self.glyphs:
                # char desconhecido: pula um espaço
                cx += int(space_width * scale)
                continue

            glyph = self.glyphs[char]
            gw, gh = glyph.get_size()

            # Escala
            if scale != 1.0:
                gw = max(1, int(gw * scale))
                gh = max(1, int(gh * scale))
                glyph = pygame.transform.scale(glyph, (gw, gh))

            # Tint: multiplica cada pixel pelo color desejado
            tinted = glyph.copy()
            tinted.fill(color + (255,), special_flags=pygame.BLEND_RGBA_MULT)

            surface.blit(tinted, (cx, y))
            cx += gw + int(self.kerning * scale)

        return cx

    def text_width(self, text: str, scale: float = 1.0, space_width: int = 18) -> int:
        """Retorna a largura em pixels que `text` ocuparia sem renderizar."""
        w = 0
        for char in text:
            if char == ' ':
                w += int(space_width * scale)
            elif char in self.glyphs:
                gw, _ = self.glyphs[char].get_size()
                w += int(gw * scale) + int(self.kerning * scale)
        return w

    def render_centered(
        self,
        surface: pygame.Surface,
        text: str,
        center_x: int,
        y: int,
        **kwargs,
    ) -> None:
        """Renderiza o texto centralizado em center_x."""
        w = self.text_width(text, scale=kwargs.get('scale', 1.0))
        self.render(surface, text, center_x - w // 2, y, **kwargs)
