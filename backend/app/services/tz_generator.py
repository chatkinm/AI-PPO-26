import re
import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
import docx
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

class TZGenerator:
    """
    Генератор официального Технического задания в формате DOCX 
    в строгом соответствии с корпоративным стандартом и шаблоном IT-компании Xpage.
    Включает 11 обязательных разделов, титульный лист, лист согласования,
    таблицы RBAC/CRUD, спецификацию методов REST API, Use Cases и NFR.
    """

    def __init__(self):
        # Поиск базового шаблона Xpage
        base_dir = Path(__file__).resolve().parent.parent.parent.parent
        self.template_path = base_dir / "Шаблон Технического задания (ТЗ) Xpage.md"
        if not self.template_path.exists():
            # Запасной путь в текущей папке проекта
            self.template_path = Path("Шаблон Технического задания (ТЗ) Xpage.md")

    def generate_docx(self, project_name: str, tz_data: Dict[str, Any], output_path: Path, project: Any = None) -> Path:
        """
        Компилирует полное ТЗ по шаблону Xpage, обогащая его структурой проекта,
        результатами анализа созвонов и прототипом FigJam.
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # 1. Загрузка базового шаблона Xpage
        if self.template_path.exists():
            md_text = self.template_path.read_text(encoding="utf-8")
        else:
            md_text = self._get_fallback_template()

        # 2. Подстановка проектных реквизитов
        today_str = datetime.datetime.now().strftime("%d.%m.%Y")
        project_id = getattr(project, "id", "2026") if project else "2026"
        
        md_text = md_text.replace("[Название продукта / Мобильное приложение / Веб-портал]", project_name)
        md_text = md_text.replace("[Название проекта Заказчика]", project_name)
        md_text = md_text.replace("[ГОД]", "2026")
        md_text = md_text.replace("[ПРОЕКТ]", str(project_id)[:8].upper())
        md_text = md_text.replace("[ДД.ММ.ГГГГ]", today_str)
        md_text = md_text.replace("[Дата]", today_str)
        md_text = md_text.replace("[Аналитик Xpage]", "Аналитик ППО Xpage")
        md_text = md_text.replace("[PM Xpage]", "Ведущий проджект-менеджер Xpage")
        md_text = md_text.replace("[Иванов И.И.]", "Иванов И.И.")
        md_text = md_text.replace("[Петров П.П.]", "Петров П.П.")
        md_text = md_text.replace("[Сидоров С.С.]", "Сидоров С.С.")
        md_text = md_text.replace("[Алексеев А.А.]", "Алексеев А.А.")
        md_text = md_text.replace("[ФИО, должность, e-mail, телефон]", "Аналитический департамент Xpage (ppo@xpage.ru)")

        # 3. Обогащение данными анализа встреч (Шаг 2)
        if project and hasattr(project, "analysis") and project.analysis:
            analysis = project.analysis
            confirmed = getattr(analysis, "confirmed_requirements", [])
            inconsistencies = getattr(analysis, "inconsistencies", [])
            
            extra_sec = "\n\n### 2.5. Результаты анализа созвонов с клиентом и согласованные требования\n\n"
            extra_sec += f"* **Индекс готовности требований (DoR):** {getattr(analysis, 'readiness_score', 90)}%\n"
            extra_sec += "* **Статус анализа:** Все ключевые технические требования согласованы в ходе предпроектного обследования.\n\n"
            
            if confirmed:
                extra_sec += "#### Реестр подтвержденных требований:\n\n"
                extra_sec += "| ID | Категория | Формулировка согласованного требования | Источник | Статус |\n"
                extra_sec += "|---|---|---|---|:---:|\n"
                for req in confirmed[:10]:
                    rid = getattr(req, "id", "REQ")
                    cat = getattr(req, "category", "Функциональное")
                    txt = getattr(req, "text", "")
                    src = getattr(req, "source", "Созвон ППО")
                    extra_sec += f"| `{rid}` | {cat} | {txt} | {src} | Согласовано |\n"
                extra_sec += "\n"

            if inconsistencies:
                extra_sec += "#### Урегулированные вопросы и уточнения клиента:\n\n"
                for inc in inconsistencies[:6]:
                    topic = getattr(inc, "topic", "Вопрос")
                    q = getattr(inc, "clarifying_question", "")
                    extra_sec += f"* **{topic}:** {q} *(Согласовано в текущей редакции ТЗ)*\n"
                extra_sec += "\n"

            # Вставляем после раздела 2.4
            if "## 3. Пользовательские роли" in md_text:
                md_text = md_text.replace("## 3. Пользовательские роли", extra_sec + "---\n\n## 3. Пользовательские роли")

        # 4. Обогащение ссылкой на интерактивную доску FigJam (Шаг 3)
        if project and getattr(project, "figjam_url", None):
            fj_note = f"\n\n> 🎨 **ИНТЕРАКТИВНЫЙ ПРОТОТИП И СХЕМА ЭКРАНОВ В FIGJAM:**\n"
            fj_note += f"> Актуальное интерактивное дерево экранов и карта переходов доступны по ссылке: `{project.figjam_url}`\n\n"
            if "## 5. Структура интерфейсов" in md_text:
                md_text = md_text.replace("## 5. Структура интерфейсов", "## 5. Структура интерфейсов" + fj_note)

        # 5. Обогащение специфическими модулями из структуры проекта (Шаг 1)
        if project and hasattr(project, "structure") and project.structure and project.structure.modules:
            project_modules = project.structure.modules
            # Проверяем, есть ли дополнительные модули, которых нет в базовом тексте
            extra_screens_text = ""
            for mod in project_modules:
                mod_name = mod.name
                if mod_name.lower() not in md_text.lower():
                    extra_screens_text += f"\n\n### 6.X. Модуль: {mod_name}\n"
                    extra_screens_text += f"* **Назначение:** {mod.description or 'Реализация функций модуля.'}\n"
                    for scr in mod.screens:
                        extra_screens_text += f"\n#### Экран «{scr.title}»\n"
                        extra_screens_text += f"* **Назначение:** {scr.purpose or 'Интерфейсный экран модуля.'}\n"
                        if scr.elements:
                            extra_screens_text += "\n| Элемент UI | Назначение и поведение |\n|---|---|\n"
                            for el in scr.elements:
                                el_name = el.name if hasattr(el, "name") else str(el)
                                el_type = getattr(el, "type", "Кнопка / Поле")
                                extra_screens_text += f"| {el_name} | Тип: {el_type}. Интерактивный элемент экрана. |\n"
                        extra_screens_text += "\n"
            
            if extra_screens_text and "## 7. Сквозные бизнес-сценарии" in md_text:
                md_text = md_text.replace("## 7. Сквозные бизнес-сценарии", extra_screens_text + "---\n\n## 7. Сквозные бизнес-сценарии")

        # 6. Компиляция в Word (.docx) через визуальный движок Xpage
        return self._render_markdown_to_docx(md_text, project_name, output_path)

    def _render_markdown_to_docx(self, md_content: str, project_name: str, output_path: Path) -> Path:
        doc = docx.Document()

        # Настройки страницы (A4, корпоративные поля Xpage)
        for section in doc.sections:
            section.top_margin = Inches(0.79)
            section.bottom_margin = Inches(0.79)
            section.left_margin = Inches(0.98)
            section.right_margin = Inches(0.59)
            
            # Header
            header = section.header
            hp = header.paragraphs[0]
            hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            hrun = hp.add_run(f"IT-компания Xpage | Техническое задание: {project_name}")
            hrun.font.name = "Arial"
            hrun.font.size = Pt(8.5)
            hrun.font.color.rgb = RGBColor(0x94, 0xA3, 0xB8)
            
            # Footer
            footer = section.footer
            fp = footer.paragraphs[0]
            fp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            frun = fp.add_run("Конфиденциально | Корпоративный стандарт разработки Xpage")
            frun.font.name = "Arial"
            frun.font.size = Pt(8.5)
            frun.font.color.rgb = RGBColor(0x94, 0xA3, 0xB8)

        lines = md_content.splitlines()
        idx = 0
        in_code_block = False
        code_lines = []

        while idx < len(lines):
            line = lines[idx]
            stripped = line.strip()

            # Кодовые блоки / Mermaid
            if stripped.startswith("```"):
                if not in_code_block:
                    in_code_block = True
                    code_lines = []
                    idx += 1
                    continue
                else:
                    in_code_block = False
                    tbl = doc.add_table(rows=1, cols=1)
                    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
                    cell = tbl.cell(0, 0)
                    self._format_cell_shading(cell, "F8FAFC")
                    self._set_cell_margins(cell, top=100, bottom=100, left=140, right=140)
                    p = cell.paragraphs[0]
                    p.paragraph_format.space_before = Pt(2)
                    p.paragraph_format.space_after = Pt(2)
                    p.paragraph_format.line_spacing = 1.05
                    run = p.add_run("\n".join(code_lines))
                    run.font.name = "Consolas"
                    run.font.size = Pt(8.5)
                    run.font.color.rgb = RGBColor(0x33, 0x41, 0x55)
                    doc.add_paragraph().paragraph_format.space_after = Pt(4)
                    idx += 1
                    continue

            if in_code_block:
                code_lines.append(line)
                idx += 1
                continue

            # Таблицы Markdown
            if stripped.startswith("|") and stripped.endswith("|"):
                table_lines = []
                while idx < len(lines) and lines[idx].strip().startswith("|") and lines[idx].strip().endswith("|"):
                    table_lines.append(lines[idx].strip())
                    idx += 1
                
                parsed_rows = []
                for tline in table_lines:
                    cleaned = tline.strip("|")
                    cells = [c.strip() for c in cleaned.split("|")]
                    if all(re.match(r"^:?-+:?$", c) for c in cells if c):
                        continue # разделительная строка таблицы
                    parsed_rows.append(cells)

                if parsed_rows:
                    num_cols = max(len(r) for r in parsed_rows)
                    tbl = doc.add_table(rows=len(parsed_rows), cols=num_cols)
                    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
                    self._set_table_borders(tbl, "CBD5E1")

                    # Повторять заголовок таблицы на каждой странице
                    header_tr = tbl.rows[0]._tr.get_or_add_trPr()
                    header_tr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))

                    for r_idx, row_data in enumerate(parsed_rows):
                        row = tbl.rows[r_idx]
                        trPr = row._tr.get_or_add_trPr()
                        trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))

                        is_header = (r_idx == 0)
                        bg_color = "1E293B" if is_header else ("F8FAFC" if r_idx % 2 == 1 else "FFFFFF")
                        text_color = RGBColor(0xFF, 0xFF, 0xFF) if is_header else RGBColor(0x1E, 0x29, 0x3B)

                        for c_idx in range(num_cols):
                            cell = row.cells[c_idx]
                            self._format_cell_shading(cell, bg_color)
                            self._set_cell_margins(cell, top=90, bottom=90, left=120, right=120)
                            val = row_data[c_idx] if c_idx < len(row_data) else ""
                            p = cell.paragraphs[0]
                            p.paragraph_format.space_before = Pt(1)
                            p.paragraph_format.space_after = Pt(1)
                            p.paragraph_format.line_spacing = 1.15
                            self._add_formatted_runs(p, val, base_font_size=9.5, base_color=text_color, base_bold=is_header)

                    doc.add_paragraph().paragraph_format.space_after = Pt(4)
                continue

            # Блоки примечаний / цитат (> ...)
            if stripped.startswith("> "):
                quote_lines = []
                while idx < len(lines) and lines[idx].strip().startswith(">"):
                    quote_lines.append(lines[idx].strip()[1:].strip())
                    idx += 1
                full_quote = " ".join(quote_lines)
                
                title = ""
                if "ИНСТРУКЦИЯ" in full_quote:
                    title = "💡 ПРИМЕЧАНИЕ АНАЛИТИКА XPAGE"
                    full_quote = full_quote.replace("💡 **ИНСТРУКЦИЯ ДЛЯ АНАЛИТИКА / PM XPAGE:**", "").replace("💡 **ИНСТРУКЦИЯ ДЛЯ АНАЛИТИКА:**", "").strip()
                elif "ПРОТОТИП" in full_quote:
                    title = "🎨 ИНТЕРАКТИВНЫЙ ПРОТОТИП FIGJAM"

                tbl = doc.add_table(rows=1, cols=1)
                tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
                cell = tbl.cell(0, 0)
                self._format_cell_shading(cell, "F0F7FF")
                borders = parse_xml(
                    f'<w:tcBorders {nsdecls("w")}>\n'
                    f'  <w:left w:val="single" w:sz="24" w:space="0" w:color="3B82F6"/>\n'
                    f'  <w:top w:val="none"/>\n'
                    f'  <w:bottom w:val="none"/>\n'
                    f'  <w:right w:val="none"/>\n'
                    f'</w:tcBorders>'
                )
                cell._tc.get_or_add_tcPr().append(borders)
                self._set_cell_margins(cell, top=100, bottom=100, left=150, right=150)
                p = cell.paragraphs[0]
                p.paragraph_format.space_before = Pt(2)
                p.paragraph_format.space_after = Pt(2)
                p.paragraph_format.line_spacing = 1.15
                if title:
                    rt = p.add_run(title + "\n")
                    rt.bold = True
                    rt.font.name = "Arial"
                    rt.font.size = Pt(9.5)
                    rt.font.color.rgb = RGBColor(0x1D, 0x4E, 0xD8)
                self._add_formatted_runs(p, full_quote, base_font_size=9.5, base_color=RGBColor(0x1E, 0x29, 0x3B))
                doc.add_paragraph().paragraph_format.space_after = Pt(4)
                continue

            # Разделительная линия
            if stripped == "---":
                p = doc.add_paragraph()
                p.paragraph_format.space_before = Pt(6)
                p.paragraph_format.space_after = Pt(6)
                idx += 1
                continue

            # Пустая строка
            if not stripped:
                idx += 1
                continue

            # Заголовки
            if stripped.startswith("# "):
                # Титульный заголовок документа
                p = doc.add_paragraph()
                p.paragraph_format.space_before = Pt(40)
                p.paragraph_format.space_after = Pt(6)
                run = p.add_run(stripped[2:])
                run.bold = True
                run.font.name = "Arial"
                run.font.size = Pt(22)
                run.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)
                idx += 1
                continue

            if stripped.startswith("## "):
                heading_text = stripped[3:]
                p = doc.add_paragraph()
                # Разрыв страницы перед каждым крупным номерным разделом
                is_main_sec = bool(re.match(r"^\d+\.", heading_text))
                if is_main_sec and not heading_text.startswith("1."):
                    doc.add_page_break()
                    p.paragraph_format.space_before = Pt(14)
                else:
                    p.paragraph_format.space_before = Pt(18)
                p.paragraph_format.space_after = Pt(6)
                p.paragraph_format.keep_with_next = True
                
                run = p.add_run(heading_text)
                run.bold = True
                run.font.name = "Arial"
                run.font.size = Pt(16)
                run.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
                idx += 1
                continue

            if stripped.startswith("### "):
                p = doc.add_paragraph()
                p.paragraph_format.space_before = Pt(14)
                p.paragraph_format.space_after = Pt(4)
                p.paragraph_format.keep_with_next = True
                run = p.add_run(stripped[4:])
                run.bold = True
                run.font.name = "Arial"
                run.font.size = Pt(13)
                run.font.color.rgb = RGBColor(0x25, 0x63, 0xEB) # Xpage Blue
                idx += 1
                continue

            if stripped.startswith("#### "):
                p = doc.add_paragraph()
                p.paragraph_format.space_before = Pt(10)
                p.paragraph_format.space_after = Pt(3)
                p.paragraph_format.keep_with_next = True
                run = p.add_run(stripped[5:])
                run.bold = True
                run.font.name = "Arial"
                run.font.size = Pt(11)
                run.font.color.rgb = RGBColor(0x33, 0x41, 0x55)
                idx += 1
                continue

            # Маркированные списки
            if stripped.startswith("* ") or stripped.startswith("- "):
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Inches(0.25)
                p.paragraph_format.space_before = Pt(1)
                p.paragraph_format.space_after = Pt(2)
                p.paragraph_format.line_spacing = 1.15
                run_bullet = p.add_run("•  ")
                run_bullet.bold = True
                run_bullet.font.name = "Arial"
                run_bullet.font.size = Pt(10)
                run_bullet.font.color.rgb = RGBColor(0x25, 0x63, 0xEB)
                self._add_formatted_runs(p, stripped[2:])
                idx += 1
                continue

            # Нумерованные списки
            num_match = re.match(r"^(\d+[\.\)])\s+(.*)", stripped)
            if num_match:
                prefix = num_match.group(1)
                rest = num_match.group(2)
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Inches(0.25)
                p.paragraph_format.space_before = Pt(2)
                p.paragraph_format.space_after = Pt(2)
                p.paragraph_format.line_spacing = 1.15
                run_num = p.add_run(prefix + " ")
                run_num.bold = True
                run_num.font.name = "Arial"
                run_num.font.size = Pt(10)
                run_num.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)
                self._add_formatted_runs(p, rest)
                idx += 1
                continue

            # Обычный абзац текста
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.line_spacing = 1.15
            self._add_formatted_runs(p, stripped)
            idx += 1

        doc.save(str(output_path))
        return output_path

    def _add_formatted_runs(self, paragraph, text: str, base_font_size: float = 10.5, base_color: RGBColor = RGBColor(0x1F, 0x29, 0x37), base_bold: bool = False):
        tokens = re.split(r"(\b\[.*?\]\(.*?\)|\*\*.*?\*\*|\*.*?\*|`.*?`)", text)
        for token in tokens:
            if not token:
                continue
            if token.startswith("**") and token.endswith("**") and len(token) >= 4:
                run = paragraph.add_run(token[2:-2])
                run.bold = True
                run.font.name = "Arial"
                run.font.size = Pt(base_font_size)
                run.font.color.rgb = base_color
            elif token.startswith("*") and token.endswith("*") and len(token) >= 2:
                run = paragraph.add_run(token[1:-1])
                run.italic = True
                run.font.name = "Arial"
                run.font.size = Pt(base_font_size)
                run.font.color.rgb = base_color
            elif token.startswith("`") and token.endswith("`") and len(token) >= 2:
                run = paragraph.add_run(token[1:-1])
                run.font.name = "Consolas"
                run.font.size = Pt(base_font_size - 1)
                run.font.color.rgb = RGBColor(0xBE, 0x18, 0x5D)
            else:
                run = paragraph.add_run(token)
                run.bold = base_bold
                run.font.name = "Arial"
                run.font.size = Pt(base_font_size)
                run.font.color.rgb = base_color

    def _set_cell_margins(self, cell, top=100, bottom=100, left=140, right=140):
        tcPr = cell._tc.get_or_add_tcPr()
        tcMar = OxmlElement("w:tcMar")
        for m, val in [("top", top), ("bottom", bottom), ("left", left), ("right", right)]:
            node = OxmlElement(f"w:{m}")
            node.set(qn("w:w"), str(val))
            node.set(qn("w:type"), "dxa")
            tcMar.append(node)
        tcPr.append(tcMar)

    def _set_table_borders(self, table, color="CBD5E1"):
        tblPr = table._tbl.tblPr
        borders = parse_xml(
            f'<w:tblBorders {nsdecls("w")}>\n'
            f'  <w:top w:val="single" w:sz="6" w:space="0" w:color="{color}"/>\n'
            f'  <w:bottom w:val="single" w:sz="6" w:space="0" w:color="{color}"/>\n'
            f'  <w:left w:val="none"/>\n'
            f'  <w:right w:val="none"/>\n'
            f'  <w:insideH w:val="single" w:sz="4" w:space="0" w:color="{color}"/>\n'
            f'  <w:insideV w:val="none"/>\n'
            f'</w:tblBorders>'
        )
        tblPr.append(borders)

    def _format_cell_shading(self, cell, hex_color: str):
        shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
        cell._tc.get_or_add_tcPr().append(shd)

    def _get_fallback_template(self) -> str:
        return "# ТЕХНИЧЕСКОЕ ЗАДАНИЕ\n## 1. Используемые термины и определения\n"

tz_generator = TZGenerator()