"""
Генератор профессиональной архитектуры экранов и функциональных блоков для FigJam
в строгом соответствии с корпоративным стандартом Xpage.
Экраны строятся как вертикальные стеки карточек (wireframes) с навигационным блоком,
модульными заголовками и ортогональными векторными связями (без стикеров и наложений).
"""

from typing import Dict, Any, List

PURPLE_HEADER = {"r": 0.486, "g": 0.227, "b": 0.929}  # #7C3AED
BLUE_HEADER = {"r": 0.145, "g": 0.388, "b": 0.922}    # #2563EB
WHITE_FILL = {"r": 1.0, "g": 1.0, "b": 1.0}           # #FFFFFF
LIGHT_BLUE_FILL = {"r": 0.941, "g": 0.969, "b": 1.0}  # #F0F7FF
CARD_STROKE = {"r": 0.796, "g": 0.835, "b": 0.882}    # #CBD5E1
CONN_BLUE = {"r": 0.231, "g": 0.510, "b": 0.965}      # #3B82F6
TEXT_WHITE = {"r": 1.0, "g": 1.0, "b": 1.0}
TEXT_DARK = {"r": 0.059, "g": 0.090, "b": 0.165}      # #0F172A

def generate_pawnshop_architecture() -> Dict[str, Any]:
    nodes: List[Dict[str, Any]] = []
    connectors: List[Dict[str, Any]] = []

    def add_node(
        node_id: str,
        title: str,
        x: float,
        y: float,
        w: float,
        h: float,
        node_type: str = "BLOCK",
        fill: Dict[str, float] = WHITE_FILL,
        text_color: Dict[str, float] = TEXT_DARK,
        stroke: Dict[str, float] = CARD_STROKE,
        font_weight: str = "Regular"
    ):
        nodes.append({
            "id": node_id,
            "title": title,
            "x": x,
            "y": y,
            "width": w,
            "height": h,
            "type": node_type,
            "fill_color": fill,
            "text_color": text_color,
            "stroke_color": stroke,
            "font_weight": font_weight
        })

    def add_connector(
        start_id: str,
        end_id: str,
        start_magnet: str = "RIGHT",
        end_magnet: str = "LEFT",
        stroke: Dict[str, float] = CONN_BLUE
    ):
        connectors.append({
            "id": f"conn_{start_id}_{end_id}",
            "start_id": start_id,
            "end_id": end_id,
            "start_magnet": start_magnet,
            "end_magnet": end_magnet,
            "stroke_color": stroke
        })

    # 1. ШАПКА: НАВИГАЦИЯ
    add_node("nav_header", "Навигация", x=220, y=-260, w=380, h=52, node_type="HEADER", fill=PURPLE_HEADER, text_color=TEXT_WHITE, font_weight="Bold")

    nav_tabs = [
        ("nav_tab_main", "Главная", 130),
        ("nav_tab_eval", "Оценки", 235),
        ("nav_tab_addr", "Адреса", 340),
        ("nav_tab_pay", "Оплата", 445),
        ("nav_tab_chat", "Чат", 550)
    ]
    for tab_id, tab_title, tab_x in nav_tabs:
        add_node(tab_id, tab_title, x=tab_x, y=-180, w=90, h=42, node_type="PILL", fill=WHITE_FILL, text_color=TEXT_DARK, font_weight="Medium")
        add_connector("nav_header", tab_id, "BOTTOM", "TOP")

    # 2. ГЛАВНЫЙ ЭКРАН (АВТОРИЗОВАННЫЙ)
    col1_x = 90
    col1_w = 260
    curr_y = -40

    add_node("scr_main_auth", "Главный экран\nАвторизованный", x=col1_x, y=curr_y, w=col1_w, h=64, node_type="HEADER", fill=PURPLE_HEADER, text_color=TEXT_WHITE, font_weight="Bold")
    add_connector("nav_tab_main", "scr_main_auth", "BOTTOM", "TOP")
    curr_y += 74

    auth_blocks = [
        ("b_prof_pers", "Профиль | Персонализация", 42, "Regular"),
        ("b_prog_loy", "Программа лояльности\n• Количество бонусов\n• Уровень программы лояльности", 68, "Regular"),
        ("b_notif", "Уведомления", 40, "Regular"),
        ("b_search", "Поиск", 40, "Regular"),
        ("b_promo", "Акции", 40, "Regular"),
        ("b_pers_promo", "Персональные акции", 40, "Regular"),
        ("b_actual", "Актуальное\nПриближающиеся сроки/платежи", 50, "Regular"),
        ("b_loan_cards", "Карточки займов", 40, "Regular"),
        ("b_store_cards", "Карточки хранения", 40, "Regular"),
        ("b_extend_all", "Продлить все", 40, "Regular"),
        ("b_loy_promo", "Программа лояльности (промо)", 42, "Regular"),
        ("b_pawn_serv", "Услуги ломбарда", 40, "Medium"),
        ("b_pledge_loans", "Займы под залог", 40, "Regular"),
        ("b_storage", "Хранение", 40, "Regular"),
        ("b_refinance", "Рефинансирование", 40, "Regular"),
        ("b_home_cash", "Деньги на дом", 40, "Regular"),
        ("b_autoloan", "Автоломбард", 40, "Regular"),
        ("b_branches", "Отделения ломбарда", 40, "Regular")
    ]
    for b_id, b_title, b_h, b_weight in auth_blocks:
        add_node(b_id, b_title, x=col1_x, y=curr_y, w=col1_w, h=b_h, font_weight=b_weight)
        curr_y += b_h + 10

    # 3. ГЛАВНЫЙ ЭКРАН (НЕ АВТОРИЗОВАННЫЙ)
    col2_x = 380
    col2_w = 260
    curr_y2 = -40

    add_node("scr_main_unauth", "Главный экран\nНе авторизованный", x=col2_x, y=curr_y2, w=col2_w, h=64, node_type="HEADER", fill=PURPLE_HEADER, text_color=TEXT_WHITE, font_weight="Bold")
    add_connector("nav_tab_main", "scr_main_unauth", "BOTTOM", "TOP")
    curr_y2 += 74

    unauth_blocks = [
        ("b_unauth_promo", "Промо авторизации/\nрегистрации", 50, "Regular"),
        ("b_unauth_notif", "Уведомления", 40, "Regular"),
        ("b_unauth_search", "Поиск", 40, "Regular"),
        ("b_unauth_promo_act", "Акции", 40, "Regular"),
        ("b_unauth_loy", "Программа лояльности (промо)", 42, "Regular"),
        ("b_unauth_services", "Услуги ломбарда", 40, "Medium"),
        ("b_unauth_pledge", "Займы под залог", 40, "Regular"),
        ("b_unauth_storage", "Хранение", 40, "Regular"),
        ("b_unauth_refinance", "Рефинансирование", 40, "Regular"),
        ("b_unauth_home", "Деньги на дом", 40, "Regular"),
        ("b_unauth_autoloan", "Автоломбард", 40, "Regular"),
        ("b_unauth_branches", "Отделения ломбарда", 40, "Regular")
    ]
    for b_id, b_title, b_h, b_weight in unauth_blocks:
        add_node(b_id, b_title, x=col2_x, y=curr_y2, w=col2_w, h=b_h, font_weight=b_weight)
        curr_y2 += b_h + 10

    # 4. ЛЕВАЯ ВЕТВЬ: УВЕДОМЛЕНИЯ И ПОИСК
    notif_x = -260
    notif_w = 240
    notif_y = 50
    add_node("scr_notif", "Уведомления", x=notif_x, y=notif_y, w=notif_w, h=52, node_type="HEADER", fill=PURPLE_HEADER, text_color=TEXT_WHITE, font_weight="Bold")
    add_connector("b_notif", "scr_notif", "LEFT", "RIGHT")

    notif_y += 62
    add_node("b_notif_list", "Список уведомлений", x=notif_x, y=notif_y, w=notif_w, h=40)
    notif_y += 50
    add_node("b_notif_push_types", "PUSH-уведомления:\n• Акции\n• Напоминания по оплате %\n• Операции по ЗБ", x=notif_x, y=notif_y, w=notif_w, h=78)
    notif_y += 88
    add_node("b_notif_hist", "История уведомлений", x=notif_x, y=notif_y, w=notif_w, h=40)

    # PUSH-Уведомления
    push_x = -560
    push_y = 50
    add_node("scr_push", "PUSH-Уведомления", x=push_x, y=push_y, w=240, h=52, node_type="HEADER", fill=PURPLE_HEADER, text_color=TEXT_WHITE, font_weight="Bold")
    add_connector("scr_notif", "scr_push", "LEFT", "RIGHT")

    push_y += 62
    add_node("b_push_create", "Создание рассылок", x=push_x, y=push_y, w=240, h=40)
    push_y += 50
    add_node("b_push_desc", "Создание рассылок по пользователям МП.\nПредусматривается добавление ссылки на\nэкран приложения, куда ведет пуш.", x=push_x, y=push_y, w=240, h=80, fill=LIGHT_BLUE_FILL)

    # Поиск
    search_x = -260
    search_w = 240
    search_y = 350
    add_node("scr_search", "Поиск", x=search_x, y=search_y, w=search_w, h=52, node_type="HEADER", fill=PURPLE_HEADER, text_color=TEXT_WHITE, font_weight="Bold")
    add_connector("b_search", "scr_search", "LEFT", "RIGHT")

    search_y += 62
    search_blocks = [
        ("b_s_input", "Строка поиска", 40),
        ("b_s_scenarios", "Ключевые сценарии", 40),
        ("b_s_pay", "Оплатить", 38),
        ("b_s_eval", "Оценить имущество", 38),
        ("b_s_more", "Дополнительно", 38),
        ("b_s_contracts", "Мои договоры", 38),
        ("b_s_map", "Карта ломбардов", 38),
        ("b_s_help", "Помощь", 38)
    ]
    for s_id, s_title, s_h in search_blocks:
        add_node(s_id, s_title, x=search_x, y=search_y, w=search_w, h=s_h)
        search_y += s_h + 8

    # Модальное окно акции
    add_node("b_modal_action", "Модальное окно акции", x=-260, y=780, w=240, h=42)
    add_connector("b_promo", "b_modal_action", "LEFT", "RIGHT")

    # 5. НИЖНИЙ ЛЕВЫЙ БЛОК: СЕРВИСЫ И УСЛУГИ ЛОМБАРДА
    serv_cols = [
        ("scr_serv_storage", "Хранение", -1100, [
            ("b_st_banner", "Баннерный блок", 40),
            ("b_st_prog", "О программе", 40),
            ("b_st_cond", "Условия хранения", 40),
            ("b_st_steps", "Как это работает? (Шаги)", 44)
        ], "b_storage"),
        ("scr_serv_refinance", "Рефинансирование займа", -860, [
            ("b_rf_banner", "Баннерный блок (+ форма заявки)", 44),
            ("b_rf_prog", "О программе", 40),
            ("b_rf_adv", "Преимущества / Выгоды", 40),
            ("b_rf_steps", "Как это работает? (Шаги)", 44)
        ], "b_refinance"),
        ("scr_serv_home", "Деньги на дом", -620, [
            ("b_hm_banner", "Баннерный блок (+ форма заявки)", 44),
            ("b_hm_prog", "О программе", 40),
            ("b_hm_steps", "Как это работает? (Шаги)", 44)
        ], "b_home_cash"),
        ("scr_serv_auto", "Автоломбард", -380, [
            ("b_at_banner", "Баннерный блок", 40),
            ("b_at_form", "Форма заявки", 40),
            ("b_at_calc", "Форма заявки с калькулятором", 44)
        ], "b_autoloan")
    ]

    for scr_id, scr_title, s_x, s_blocks, main_b_id in serv_cols:
        s_y = 860
        add_node(scr_id, scr_title, x=s_x, y=s_y, w=220, h=50, node_type="HEADER", fill=BLUE_HEADER, text_color=TEXT_WHITE, font_weight="Bold")
        add_connector(main_b_id, scr_id, "LEFT", "RIGHT")
        s_y += 60
        for sb_id, sb_title, sb_h in s_blocks:
            add_node(sb_id, sb_title, x=s_x, y=s_y, w=220, h=sb_h)
            s_y += sb_h + 8

    # 6. ПРАВАЯ ВЕТВЬ: ОЦЕНКА ИМУЩЕСТВА (ЧАТ С ИИ)
    eval_x = 730
    eval_y = -120
    add_node("scr_eval", "Оценка имущества", x=eval_x, y=eval_y, w=270, h=52, node_type="HEADER", fill=PURPLE_HEADER, text_color=TEXT_WHITE, font_weight="Bold")
    add_connector("nav_tab_eval", "scr_eval", "RIGHT", "LEFT")

    eval_y += 64
    add_node(
        "b_eval_chat",
        "Чат с ИИ\nПри входе через оценку автоматически формируется\nзапрос на оценку имущества и осуществляется\nначало диалога по оценке имущества",
        x=eval_x, y=eval_y, w=270, h=95,
        fill=WHITE_FILL
    )
    add_connector("scr_eval", "b_eval_chat", "BOTTOM", "TOP")

    req_data_x = 1060
    req_data_y = eval_y
    add_node(
        "b_eval_req_data",
        "Запрос данных пользователя\nИИ запрашивает:\n1. Имя\n2. Телефон\n*Фиксируется в заявку",
        x=req_data_x, y=req_data_y, w=240, h=95,
        fill=LIGHT_BLUE_FILL
    )
    add_connector("b_eval_chat", "b_eval_req_data", "RIGHT", "LEFT")

    # Ветка 1: Ювелирные изделия
    jewel_x = 1360
    jewel_y = -180
    add_node("b_jewel_hdr", "Определение типа: Ювелирное изделие", x=jewel_x, y=jewel_y, w=270, h=44, node_type="PILL", fill=PURPLE_HEADER, text_color=TEXT_WHITE, font_weight="Medium")
    add_connector("b_eval_req_data", "b_jewel_hdr", "RIGHT", "LEFT")

    jewel_y += 54
    add_node("b_jewel_params", "Уточнение информации:\nТип изделия (кольцо, цепочка...)\nМатериал (золото, серебро)\nПроба, Чистый вес, Дефекты", x=jewel_x, y=jewel_y, w=270, h=86)
    add_connector("b_jewel_hdr", "b_jewel_params", "BOTTOM", "TOP")

    jewel_y += 96
    add_node("b_jewel_calc", "Предварительная оценка:\nОценка вещи: 45 000–55 000 ₽\nВозможная сумма займа: 30 000–40 000 ₽\nОриентировочный расчет ставки и %", x=jewel_x, y=jewel_y, w=270, h=86, fill=LIGHT_BLUE_FILL)
    add_connector("b_jewel_params", "b_jewel_calc", "BOTTOM", "TOP")

    jewel_y += 96
    add_node("b_jewel_crm", "Уведомление о передаче в ИС:\nФорма с данными передается в CRM\nМенеджер подключается к чату\nПамятка клиенту: паспорт, упаковка, бирки", x=jewel_x, y=jewel_y, w=270, h=86)
    add_connector("b_jewel_calc", "b_jewel_crm", "BOTTOM", "TOP")

    # Ветка 2: Техника
    tech_x = 1360
    tech_y = 150
    add_node("b_tech_hdr", "Определение типа: Техника", x=tech_x, y=tech_y, w=270, h=44, node_type="PILL", fill=BLUE_HEADER, text_color=TEXT_WHITE, font_weight="Medium")
    add_connector("b_eval_req_data", "b_tech_hdr", "RIGHT", "LEFT")

    tech_y += 54
    add_node("b_tech_params", "Уточнение информации:\nТип изделия (ноутбук, смартфон...)\nФирма (Apple, Samsung...), Объем памяти\nДефекты, Комплектность, Документы", x=tech_x, y=tech_y, w=270, h=86)
    add_connector("b_tech_hdr", "b_tech_params", "BOTTOM", "TOP")

    tech_y += 96
    add_node("b_tech_calc", "Предварительная оценка:\nРасчет стоимости на основе параметров\nОриентировочная сумма и срок займа", x=tech_x, y=tech_y, w=270, h=76, fill=LIGHT_BLUE_FILL)
    add_connector("b_tech_params", "b_tech_calc", "BOTTOM", "TOP")

    tech_y += 86
    add_node("b_tech_crm", "Передача заявки специалисту:\nРезультат оценки в ЛК в «Имущество»\nСсылка на карту ломбардов для визита", x=tech_x, y=tech_y, w=270, h=76)
    add_connector("b_tech_calc", "b_tech_crm", "BOTTOM", "TOP")

    # 7. ПРАВЫЙ НИЖНИЙ БЛОК: ОПЛАТА, АВТОРИЗАЦИЯ, ДОГОВОРЫ, ПРОФИЛЬ, БОНУСЫ, АДРЕСА
    pay_x = 730
    pay_y = 170
    add_node("scr_pay", "Оплата", x=pay_x, y=pay_y, w=260, h=50, node_type="HEADER", fill=PURPLE_HEADER, text_color=TEXT_WHITE, font_weight="Bold")
    add_connector("nav_tab_pay", "scr_pay", "RIGHT", "LEFT")

    pay_y += 60
    pay_blocks = [
        ("b_pay_auth", "Для авторизованных: Выбор ЗБ/хранения", 42),
        ("b_pay_unauth", "Для неавторизованных: Ввод № ЗБ", 42),
        ("b_pay_flow", "Сценарий оплаты / Банк-эквайер", 42),
        ("b_pay_status", "Экран статуса оплаты (Успех / ЧАВО)", 42)
    ]
    for pb_id, pb_title, pb_h in pay_blocks:
        add_node(pb_id, pb_title, x=pay_x, y=pay_y, w=260, h=pb_h)
        pay_y += pb_h + 8

    # Авторизация / Регистрация
    auth_x = 730
    auth_y = 440
    add_node("scr_auth", "Авторизация / Регистрация", x=auth_x, y=auth_y, w=260, h=50, node_type="HEADER", fill=PURPLE_HEADER, text_color=TEXT_WHITE, font_weight="Bold")
    add_connector("b_unauth_promo", "scr_auth", "RIGHT", "LEFT")

    auth_y += 60
    auth_flow = [
        ("b_au_splash", "Splash экран", 38),
        ("b_au_phone", "Шаг 1 - Ввод телефона / Биометрия", 42),
        ("b_au_code", "Шаг 2 - Ввод кода (PUSH/Звонок/СМС)", 42),
        ("b_au_reg", "Шаг 2 - Регистрация (ФИО, E-mail, ПД)", 42),
        ("b_au_enter", "Вход в МП", 38)
    ]
    for ab_id, ab_title, ab_h in auth_flow:
        add_node(ab_id, ab_title, x=auth_x, y=auth_y, w=260, h=ab_h)
        auth_y += ab_h + 8

    # Мои договоры
    con_x = 1040
    con_y = 390
    add_node("scr_contracts", "Мои договоры", x=con_x, y=con_y, w=260, h=50, node_type="HEADER", fill=PURPLE_HEADER, text_color=TEXT_WHITE, font_weight="Bold")
    add_connector("b_actual", "scr_contracts", "RIGHT", "LEFT")

    con_y += 60
    con_blocks = [
        ("b_c_tabs", "Разделы: Займы | Хранение | Архив", 40),
        ("b_c_active_loan", "Активный заём (№, QR, дата, срок, %)", 46),
        ("b_c_loan_actions", "Функционал ЗБ: Продлить/Оплатить %\nЗакрыть и перевести на хранение", 56),
        ("b_c_active_store", "Договор хранения (№, QR, оценка, ДО)", 46),
        ("b_c_store_actions", "Функционал хранения: Продлить / В залог", 44)
    ]
    for cb_id, cb_title, cb_h in con_blocks:
        add_node(cb_id, cb_title, x=con_x, y=con_y, w=260, h=cb_h)
        con_y += cb_h + 8

    # Профиль
    prof_x = 1040
    prof_y = 700
    add_node("scr_profile", "Профиль", x=prof_x, y=prof_y, w=260, h=50, node_type="HEADER", fill=PURPLE_HEADER, text_color=TEXT_WHITE, font_weight="Bold")
    add_connector("b_prof_pers", "scr_profile", "RIGHT", "LEFT")

    prof_y += 60
    prof_blocks = [
        ("b_pr_greet", "Приветствие и статус пользователя", 40),
        ("b_pr_loy", "Программа лояльности (Уровень, баллы)", 42),
        ("b_pr_settings", "Настройки: ПЭП, Биометрия, PUSH", 42),
        ("b_pr_goods", "Мое имущество (оцененное/хранение)", 42),
        ("b_pr_info", "Полезное: Отделения, Отзывы, Помощь", 42),
        ("b_pr_exit", "Выйти из профиля", 38)
    ]
    for pb_id, pb_title, pb_h in prof_blocks:
        add_node(pb_id, pb_title, x=prof_x, y=prof_y, w=260, h=pb_h)
        prof_y += pb_h + 8

    # Бонусы
    bon_x = 1360
    bon_y = 520
    add_node("scr_bonuses", "Бонусы", x=bon_x, y=bon_y, w=240, h=50, node_type="HEADER", fill=PURPLE_HEADER, text_color=TEXT_WHITE, font_weight="Bold")
    add_connector("b_prog_loy", "scr_bonuses", "RIGHT", "LEFT")

    bon_y += 60
    bon_blocks = [
        ("b_bn_balance", "Баланс бонусов", 38),
        ("b_bn_history", "История начислений / списаний", 40),
        ("b_bn_about", "О бонусной программе / Выгоды", 40),
        ("b_bn_usage", "Как использовать бонусы", 38)
    ]
    for bb_id, bb_title, bb_h in bon_blocks:
        add_node(bb_id, bb_title, x=bon_x, y=bon_y, w=240, h=bb_h)
        bon_y += bb_h + 8

    # Адреса ломбардов
    addr_x = 1360
    addr_y = 740
    add_node("scr_branches", "Адреса ломбардов", x=addr_x, y=addr_y, w=240, h=50, node_type="HEADER", fill=PURPLE_HEADER, text_color=TEXT_WHITE, font_weight="Bold")
    add_connector("nav_tab_addr", "scr_branches", "RIGHT", "LEFT")
    add_connector("b_branches", "scr_branches", "RIGHT", "LEFT")

    addr_y += 60
    addr_blocks = [
        ("b_ad_filter", "Фильтрация: На карте / Списком", 40),
        ("b_ad_map", "Карта ломбардов (отделения, режим)", 44),
        ("b_ad_route", "Построение маршрута (2ГИС / Яндекс)", 40)
    ]
    for ab_id, ab_title, ab_h in addr_blocks:
        add_node(ab_id, ab_title, x=addr_x, y=addr_y, w=240, h=ab_h)
        addr_y += ab_h + 8

    return {
        "status": "success",
        "total_nodes": len(nodes),
        "total_connectors": len(connectors),
        "nodes": nodes,
        "connectors": connectors
    }

def generate_dynamic_vertical_architecture(project: Any) -> Dict[str, Any]:
    nodes: List[Dict[str, Any]] = []
    connectors: List[Dict[str, Any]] = []

    def add_node(
        node_id: str,
        title: str,
        x: float,
        y: float,
        w: float,
        h: float,
        node_type: str = "BLOCK",
        fill: Dict[str, float] = WHITE_FILL,
        text_color: Dict[str, float] = TEXT_DARK,
        stroke: Dict[str, float] = CARD_STROKE,
        font_weight: str = "Regular"
    ):
        nodes.append({
            "id": node_id,
            "title": title,
            "x": x,
            "y": y,
            "width": w,
            "height": h,
            "type": node_type,
            "fill_color": fill,
            "text_color": text_color,
            "stroke_color": stroke,
            "font_weight": font_weight
        })

    def add_connector(
        start_id: str,
        end_id: str,
        start_magnet: str = "RIGHT",
        end_magnet: str = "LEFT",
        stroke: Dict[str, float] = CONN_BLUE
    ):
        connectors.append({
            "id": f"conn_{start_id}_{end_id}",
            "start_id": start_id,
            "end_id": end_id,
            "start_magnet": start_magnet,
            "end_magnet": end_magnet,
            "stroke_color": stroke
        })

    project_title = project.structure.project_name if project.structure else project.name
    add_node(
        "nav_main_header",
        f"Навигация: {project_title}",
        x=200, y=-220, w=460, h=54,
        node_type="HEADER",
        fill=PURPLE_HEADER,
        text_color=TEXT_WHITE,
        font_weight="Bold"
    )

    modules = project.structure.modules if project.structure else []
    col_width = 280
    col_gap = 50
    start_x = 0

    all_screens = []
    for mod in modules:
        for scr in mod.screens:
            all_screens.append((mod, scr))

    num_screens = len(all_screens)
    screens_per_row = max(3, min(5, num_screens // 2 if num_screens > 6 else num_screens))
    
    for idx, (mod, scr) in enumerate(all_screens):
        col = idx % screens_per_row
        row = idx // screens_per_row

        col_x = start_x + (col * (col_width + col_gap))
        col_y = (row * 650) - 100

        scr_node_id = f"scr_dyn_{scr.id}"
        add_node(
            scr_node_id,
            f"{scr.title}\n[{mod.name}]",
            x=col_x, y=col_y, w=col_width, h=62,
            node_type="HEADER",
            fill=PURPLE_HEADER if "главн" in scr.title.lower() or "нав" in scr.title.lower() else BLUE_HEADER,
            text_color=TEXT_WHITE,
            font_weight="Bold"
        )

        add_connector("nav_main_header", scr_node_id, "BOTTOM", "TOP")

        curr_y = col_y + 72
        if scr.elements:
            for elem_idx, elem in enumerate(scr.elements):
                elem_id = f"elem_dyn_{scr.id}_{elem_idx}"
                elem_title = elem.name
                elem_h = 42
                if len(elem_title) > 30:
                    elem_h = 58
                add_node(
                    elem_id,
                    elem_title,
                    x=col_x, y=curr_y, w=col_width, h=elem_h,
                    node_type="BLOCK"
                )
                curr_y += elem_h + 8
        else:
            placeholder_id = f"ph_dyn_{scr.id}"
            add_node(
                placeholder_id,
                scr.purpose or "Контентный блок экрана",
                x=col_x, y=curr_y, w=col_width, h=48,
                node_type="BLOCK"
            )

    return {
        "status": "success",
        "total_nodes": len(nodes),
        "total_connectors": len(connectors),
        "nodes": nodes,
        "connectors": connectors
    }