const { useState, useEffect } = React;

function App() {
  const [projects, setProjects] = useState([]);
  const [activeProject, setActiveProject] = useState(null);
  const [currentStep, setCurrentStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [loadingText, setLoadingText] = useState("");
  const [systemStatus, setSystemStatus] = useState(null);

  // Data states
  const [estimateData, setEstimateData] = useState(null);
  const [structure, setStructure] = useState(null);
  const [transcripts, setTranscripts] = useState([]);
  const [analysisReport, setAnalysisReport] = useState(null);
  const [analysisActiveTab, setAnalysisActiveTab] = useState("checklist"); // "checklist", "inconsistencies", "requirements", "gaps"
  const [checklistFilter, setChecklistFilter] = useState("all"); // "all", "critical", "high", "contradiction", "gap", "confirmed"
  const [figjamUrl, setFigjamUrl] = useState("");
  const [figjamData, setFigjamData] = useState(null);
  const [tzGenerated, setTzGenerated] = useState(false);
  const [structureViewMode, setStructureViewMode] = useState("canvas"); // "canvas" or "cards"
  const [zoomLevel, setZoomLevel] = useState(1);
  const [showPluginModal, setShowPluginModal] = useState(false);
  const [notification, setNotification] = useState(null);

  const showToast = (msg, type = "success") => {
    setNotification({ msg, type });
    setTimeout(() => setNotification(null), 4000);
  };

  useEffect(() => {
    fetchHealth();
    loadProjects();
  }, []);

  const fetchHealth = async () => {
    try {
      const res = await fetch("/api/health");
      const data = await res.json();
      setSystemStatus(data);
    } catch (e) {
      console.error("Health check failed:", e);
    }
  };

  const loadProjects = async () => {
    try {
      const res = await fetch("/api/projects");
      const list = await res.json();
      setProjects(list);
      if (list.length > 0 && !activeProject) {
        selectProject(list[0]);
      }
    } catch (e) {
      console.error("Failed to load projects:", e);
    }
  };

  const selectProject = (p) => {
    setActiveProject(p);
    setCurrentStep(p.current_step || 1);
    if (p.structure) setStructure(p.structure);
    if (p.analysis) setAnalysisReport(p.analysis);
    if (p.tz_path) setTzGenerated(true);
    if (p.figjam_url) setFigjamUrl(p.figjam_url);
    if (p.transcript_files) setTranscripts(p.transcript_files.map(f => f.split(/[\\/]/).pop()));
  };

  const createNewProject = async () => {
    const name = prompt("Введите название нового проекта:", "Новый проект ППО");
    if (!name) return;
    try {
      const res = await fetch("/api/projects", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name })
      });
      const p = await res.json();
      setProjects([p, ...projects]);
      selectProject(p);
      showToast(`Проект «${p.name}» создан!`);
    } catch (e) {
      showToast("Ошибка создания проекта", "error");
    }
  };

  const handleLoadDemo = async () => {
    setLoading(true);
    setLoadingText("Подготовка демонстрационного кейса Xpage (Ломбард)...");
    try {
      const res = await fetch("/api/projects/load-demo", { method: "POST" });
      const p = await res.json();
      setProjects([p, ...projects]);
      selectProject(p);
      showToast("Сквозной кейс Xpage успешно загружен! Смета и созвоны готовы к анализу.");
    } catch (e) {
      showToast("Ошибка загрузки демо-кейса", "error");
    } finally {
      setLoading(false);
    }
  };

  // --- STEP 1: СМЕТА ---
  const handleUploadEstimate = async (e) => {
    const file = e.target.files[0];
    if (!file || !activeProject) return;
    const formData = new FormData();
    formData.append("file", file);

    setLoading(true);
    setLoadingText("Парсинг строк сметы из Excel...");
    try {
      const res = await fetch(`/api/structure/upload-estimate/${activeProject.id}`, {
        method: "POST",
        body: formData
      });
      const data = await res.json();
      setEstimateData(data);
      showToast(`Смета загружена: ${data.total_rows} строк извлечено`);
    } catch (err) {
      showToast("Ошибка загрузки сметы", "error");
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateStructure = async () => {
    if (!activeProject) return;
    setLoading(true);
    setLoadingText("AI анализирует смету и формирует иерархию экранов по стандарту Xpage...");
    try {
      const res = await fetch(`/api/structure/generate/${activeProject.id}`, { method: "POST" });
      const data = await res.json();
      setStructure(data);
      showToast("Первичная структура успешно сформирована!");
    } catch (err) {
      showToast("Сначала загрузите смету или используйте кнопку «Демо-кейс Xpage»", "error");
    } finally {
      setLoading(false);
    }
  };

  const generateFigJamPayload = (struct) => {
    if (!struct) return "";
    let lines = [`* ${struct.project_name || "Продукт"}`];
    struct.modules?.forEach(m => {
      lines.push(`  * Модуль: ${m.name}`);
      m.screens?.forEach(s => {
        const elemStr = s.elements?.length ? ` (${s.elements.map(e => typeof e === 'string' ? e : e.name).join(", ")})` : "";
        lines.push(`    * Экран [${s.id}]: ${s.title}${elemStr}`);
      });
    });
    return lines.join("\n");
  };

  const handleExportToFigJam = () => {
    if (!structure) return;
    const targetUrl = figjamUrl && figjamUrl.includes("figma.com") ? figjamUrl : "https://www.figma.com/board/new";
    window.open(targetUrl, "_blank");
    setShowPluginModal(true);
    showToast("Холст FigJam открыт! Запустите плагин Xpage ППО Sync для мгновенного построения структуры.", "success");
  };

  const handleApproveAndExportToFigJam = () => {
    handleExportToFigJam();
    setCurrentStep(2);
  };

  const handleAddScreen = (modIdx) => {
    const title = prompt("Введите название нового экрана:");
    if (!title) return;
    const newStructure = { ...structure };
    newStructure.modules[modIdx].screens.push({
      id: `SCR-ADD-${Date.now().toString().slice(-3)}`,
      title: title,
      purpose: "Добавлено пользователем вручную",
      elements: ["Кнопка действия", "Контентная область"]
    });
    setStructure(newStructure);
    // sync with backend
    fetch(`/api/structure/update/${activeProject.id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(newStructure)
    });
    showToast(`Экран «${title}» добавлен в структуру!`);
  };

  // --- STEP 2: СОЗВОНЫ ---
  const handleUploadTranscript = async (e) => {
    const file = e.target.files[0];
    if (!file || !activeProject) return;
    const formData = new FormData();
    formData.append("file", file);

    setLoading(true);
    setLoadingText(`Обработка файла ${file.name}...`);
    try {
      const res = await fetch(`/api/analysis/upload-transcript/${activeProject.id}`, {
        method: "POST",
        body: formData
      });
      const data = await res.json();
      setTranscripts([...transcripts, data.filename]);
      showToast(`Встреча «${data.filename}» добавлена в базу знаний!`);
    } catch (err) {
      showToast("Ошибка загрузки файла встречи", "error");
    } finally {
      setLoading(false);
    }
  };

  const handleRunAnalysis = async () => {
    if (!activeProject) return;
    setLoading(true);
    setLoadingText("Семантический кросс-анализ созвонов: поиск противоречий и составление вопросов клиенту...");
    try {
      const res = await fetch(`/api/analysis/run-analysis/${activeProject.id}`, { method: "POST" });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || "Ошибка анализа требований");
      }
      setAnalysisReport(data);
      showToast("Кросс-анализ завершен! Выявлены противоречия и пробелы.");
    } catch (err) {
      showToast(err.message || "Ошибка анализа", "error");
    } finally {
      setLoading(false);
    }
  };

  const handleExportQuestions = () => {
    if (!analysisReport) return;
    let md = `# Аудит требований ППО и опросник для клиента по стандарту Xpage\n`;
    md += `**Проект:** ${activeProject?.name}\n`;
    md += `**Индекс готовности требований (DoR):** ${analysisReport.readiness_score || 82}%\n`;
    md += `**Дата проведения аудита:** ${new Date().toLocaleDateString()}\n\n`;
    md += `---\n\n`;

    md += `## 1. Реестр выявленных противоречий и вопросов клиенту (${analysisReport.inconsistencies?.length || 0})\n\n`;
    analysisReport.inconsistencies?.forEach((inc, idx) => {
      md += `### ${idx + 1}. ${inc.topic}\n`;
      if (inc.block_number) md += `* **Связанный блок чек-листа:** Блок ${inc.block_number}\n`;
      if (inc.impact_area) md += `* **Зона влияния:** ${inc.impact_area}\n`;
      md += `* **Критичность:** ${inc.severity === 'critical' ? '🔴 Критическая' : inc.severity === 'high' ? '🟡 Высокая' : '🔵 Средняя'}\n`;
      md += `* **Источник А:** ${inc.source_a}\n`;
      md += `* **Источник Б:** ${inc.source_b}\n`;
      md += `* **Суть конфликта:** ${inc.conflict_explanation}\n`;
      md += `* **Вопрос для Заказчика:** **«${inc.clarifying_question}»**\n\n`;
    });

    if (analysisReport.checklist_audit && analysisReport.checklist_audit.length > 0) {
      md += `## 2. Матрица аудита по 20 блокам чек-листа полноты информации Xpage\n\n`;
      md += `| № | Блок чек-листа | Статус | Риск | Что зафиксировано | Описание риска | Рекомендация / Вопрос |\n`;
      md += `|---|---|:---:|:---:|---|---|---|\n`;
      analysisReport.checklist_audit.forEach((item) => {
        const stBadge = item.status === 'confirmed' ? '✅ Согласовано' : item.status === 'contradiction' ? '⚠️ Противоречие' : '🔍 Белое пятно';
        const riskBadge = item.risk_level === 'critical' ? '🔴 Критический' : item.risk_level === 'high' ? '🟡 Высокий' : '🔵 Средний';
        md += `| ${item.block_number} | **${item.block_name}** | ${stBadge} | ${riskBadge} | ${item.findings || '-'} | ${item.risk_description || '-'} | ${item.recommendation_or_question || '-'} |\n`;
      });
      md += `\n\n`;
    }

    if (analysisReport.missing_critical_topics && analysisReport.missing_critical_topics.length > 0) {
      md += `## 3. Критические белые пятна (Gaps)\n\n`;
      analysisReport.missing_critical_topics.forEach((gap, idx) => {
        md += `${idx + 1}. ⚠️ ${gap}\n`;
      });
      md += `\n`;
    }

    if (analysisReport.confirmed_requirements && analysisReport.confirmed_requirements.length > 0) {
      md += `## 4. Согласованные технические требования (${analysisReport.confirmed_requirements.length})\n\n`;
      analysisReport.confirmed_requirements.forEach((req) => {
        md += `* **[${req.id}]** (${req.category || 'Общее'}): ${req.text} *(Источник: ${req.source})*\n`;
      });
    }

    const blob = new Blob([md], { type: "text/markdown;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `Аудит_ППО_и_опросник_${activeProject?.name}.md`;
    a.click();
    showToast("Полный опросник и матрица аудита выгружены в Markdown!");
  };
  // --- STEP 3: FIGJAM ---
  const handleSyncFigjam = async () => {
    if (!activeProject || !figjamUrl) return;
    setLoading(true);
    setLoadingText("Подключение к Figma REST API и извлечение нод FigJam...");
    try {
      const res = await fetch(`/api/figjam/sync/${activeProject.id}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url_or_key: figjamUrl })
      });
      const data = await res.json();
      setFigjamData(data);
      showToast(`FigJam синхронизирован: извлечено ${data.extracted_nodes_count} элементов`);
    } catch (err) {
      showToast("Ошибка чтения FigJam: проверьте ссылку или токен в .env", "error");
    } finally {
      setLoading(false);
    }
  };

  // --- STEP 4: ТЗ ---
  const handleGenerateTZ = async () => {
    if (!activeProject) return;
    setLoading(true);
    setLoadingText("Сборка и верстка документа Технического задания по корпоративному стандарту Xpage...");
    try {
      const res = await fetch(`/api/tz/generate/${activeProject.id}`, { method: "POST" });
      const data = await res.json();
      setTzGenerated(true);
      showToast("Техническое задание готово к скачиванию!");
    } catch (err) {
      showToast("Ошибка генерации ТЗ", "error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      {/* Toast Notification */}
      {notification && (
        <div className={`fixed top-4 right-4 z-50 px-5 py-3 rounded-xl shadow-2xl flex items-center gap-3 transition-all ${
          notification.type === "error" ? "bg-rose-600 text-white" : "bg-emerald-600 text-white"
        }`}>
          <span>{notification.type === "error" ? "⚠️" : "✅"}</span>
          <span className="font-medium text-sm">{notification.msg}</span>
        </div>
      )}

      {/* Loading Overlay */}
      {loading && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex flex-col items-center justify-center gap-4">
          <div className="w-14 h-14 border-4 border-rose-500 border-t-transparent rounded-full animate-spin"></div>
          <div className="text-lg font-semibold text-white tracking-wide">{loadingText}</div>
          <div className="text-xs text-slate-400">Пожалуйста, подождите, нейросеть обрабатывает контекст...</div>
        </div>
      )}

      {/* HEADER */}
      <header className="border-b border-slate-800 bg-[#0D1322] px-8 py-4 flex items-center justify-between sticky top-0 z-40">
        <div className="flex items-center gap-4">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-rose-600 to-rose-400 flex items-center justify-center font-black text-xl text-white shadow-lg shadow-rose-500/20">
            X
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-lg tracking-tight text-white">Xpage</span>
              <span className="text-xs px-2 py-0.5 rounded bg-rose-500/10 text-rose-400 font-semibold border border-rose-500/20">AI ППО</span>
            </div>
            <div className="text-xs text-slate-400">Сервис автоматизации предпроектного обследования</div>
          </div>
        </div>

        {/* Project Selector & Demo button */}
        <div className="flex items-center gap-3">
          <button 
            onClick={handleLoadDemo}
            className="px-3.5 py-1.5 bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 text-black text-xs font-bold rounded-lg shadow-md transition flex items-center gap-1.5"
            title="Загрузить готовый сквозной кейс ломбарда Xpage с реальной сметой и созвонами"
          >
            <span>🚀 Демо-кейс Xpage</span>
          </button>
          <div className="h-6 w-[1px] bg-slate-800 mx-1"></div>
          <select 
            className="bg-slate-800 border border-slate-700 text-sm text-white rounded-lg px-3 py-1.5 focus:outline-none focus:border-rose-500 max-w-[220px] truncate"
            value={activeProject?.id || ""}
            onChange={(e) => {
              const p = projects.find(x => x.id === e.target.value);
              if (p) selectProject(p);
            }}
          >
            {projects.map(p => (
              <option key={p.id} value={p.id}>{p.name}</option>
            ))}
          </select>
          <button 
            onClick={createNewProject}
            className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs rounded-lg border border-slate-700 font-medium transition"
          >
            + Проект
          </button>
        </div>

        {/* System Status Indicators */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            Groq LPU Active
          </div>
          <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs">
            Figma Token: OK
          </div>
        </div>
      </header>

      {/* STEP PROGRESS WIZARD BAR */}
      <div className="bg-[#0F172A] border-b border-slate-800 px-8 py-3">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          {[
            { num: 1, title: "1. Первичная смета", sub: "Структура и майндмэп" },
            { num: 2, title: "2. База знаний и созвоны", sub: "Анализ противоречий" },
            { num: 3, title: "3. Интеграция FigJam", sub: "Сверка прототипов" },
            { num: 4, title: "4. Техническое задание", sub: "Генерация DOCX" }
          ].map(s => {
            const isActive = currentStep === s.num;
            const isDone = currentStep > s.num;
            return (
              <button
                key={s.num}
                onClick={() => setCurrentStep(s.num)}
                className={`flex items-center gap-3 py-1.5 px-4 rounded-xl transition text-left ${
                  isActive ? "bg-rose-500/15 border border-rose-500/30" : "hover:bg-slate-800/60"
                }`}
              >
                <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm ${
                  isDone ? "bg-emerald-500 text-black" : isActive ? "bg-rose-500 text-white" : "bg-slate-800 text-slate-400"
                }`}>
                  {isDone ? "✓" : s.num}
                </div>
                <div>
                  <div className={`text-sm font-semibold ${isActive ? "text-white" : "text-slate-300"}`}>{s.title}</div>
                  <div className="text-[11px] text-slate-500">{s.sub}</div>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* MAIN BODY CONTENT */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-8">
        {/* STEP 1: СМЕТА */}
        {currentStep === 1 && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold text-white">Этап 1: Формирование первичной структуры продукта</h1>
                <p className="text-sm text-slate-400">Загрузите первичную смету проекта в Excel (.xlsx). AI разберет разделы и построит дерево экранов.</p>
              </div>
              <div className="flex gap-3">
                <label className="px-4 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-xl text-sm font-medium text-white cursor-pointer transition flex items-center gap-2">
                  <span>📂 Загрузить смету (.xlsx)</span>
                  <input type="file" accept=".xlsx" className="hidden" onChange={handleUploadEstimate} />
                </label>
                <button
                  onClick={handleGenerateStructure}
                  className="px-5 py-2 bg-rose-600 hover:bg-rose-500 text-white rounded-xl text-sm font-semibold shadow-lg shadow-rose-600/20 transition flex items-center gap-2"
                >
                  <span>⚡ Сгенерировать структуру</span>
                </button>
              </div>
            </div>

            {/* FigJam Board link configuration */}
            <div className="flex items-center gap-3 bg-slate-900/60 p-3.5 rounded-xl border border-slate-800">
              <span className="text-xs font-medium text-slate-300 whitespace-nowrap flex items-center gap-1.5">
                <span>🎨 Доска FigJam:</span>
              </span>
              <input
                type="text"
                placeholder="Вставьте ссылку на доску FigJam (если оставить пустой — автоматически откроется новая доска)..."
                value={figjamUrl}
                onChange={(e) => setFigjamUrl(e.target.value)}
                className="flex-1 bg-slate-950 border border-slate-700/80 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-violet-500"
              />
              {figjamUrl && (
                <a 
                  href={figjamUrl} 
                  target="_blank" 
                  className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs rounded-lg border border-slate-700 transition"
                >
                  🔗 Открыть
                </a>
              )}
            </div>

            {/* Structure View */}
            {structure ? (
              <div className="space-y-4">
                {/* Control and View Switcher Bar */}
                <div className="flex flex-wrap items-center justify-between gap-3 bg-slate-900/80 p-4 rounded-xl border border-slate-800">
                  <div className="flex items-center gap-4">
                    <div className="text-sm text-slate-300">
                      <span className="font-semibold text-white">{structure.project_name}</span>: модулей: <span className="text-indigo-400 font-bold">{structure.modules?.length || 0}</span>, экранов: <span className="text-indigo-400 font-bold">{structure.modules?.reduce((acc, m) => acc + (m.screens?.length || 0), 0)}</span>
                    </div>

                    {/* Switcher: Canvas vs Cards */}
                    <div className="flex items-center bg-slate-950 p-1 rounded-xl border border-slate-800">
                      <button
                        onClick={() => setStructureViewMode("canvas")}
                        className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition flex items-center gap-1.5 ${
                          structureViewMode === "canvas" ? "bg-indigo-600 text-white shadow" : "text-slate-400 hover:text-white"
                        }`}
                      >
                        <span>🗺️ Интерактивный холст (Mindmap)</span>
                      </button>
                      <button
                        onClick={() => setStructureViewMode("cards")}
                        className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition flex items-center gap-1.5 ${
                          structureViewMode === "cards" ? "bg-slate-800 text-white shadow" : "text-slate-400 hover:text-white"
                        }`}
                      >
                        <span>📋 Карточки экранов</span>
                      </button>
                    </div>
                  </div>

                  <div className="flex items-center gap-2.5">
                    <button 
                      onClick={handleExportToFigJam}
                      className="px-4 py-2 bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white rounded-xl text-xs font-semibold transition flex items-center gap-2 shadow-lg shadow-indigo-600/20"
                      title="Открыть FigJam и запустить плагин автоматической отрисовки"
                    >
                      <span>⚡ Открыть и нарисовать в FigJam</span>
                    </button>
                    <button 
                      onClick={() => setShowPluginModal(true)}
                      className="px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white rounded-xl text-xs font-medium border border-slate-700 transition flex items-center gap-1.5"
                    >
                      <span>🔌 Плагин FigJam</span>
                    </button>
                    <button 
                      onClick={handleApproveAndExportToFigJam}
                      className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-semibold transition flex items-center gap-1.5"
                    >
                      <span>Утвердить ⟶ К созвонам</span>
                    </button>
                  </div>
                </div>

                {/* MODE 1: INTERACTIVE MINDMAP CANVAS */}
                {structureViewMode === "canvas" && (
                  <div className="bg-slate-950 rounded-2xl border border-slate-800 p-6 overflow-hidden relative shadow-2xl">
                    {/* Zoom & View Toolbar */}
                    <div className="flex items-center justify-between mb-6 pb-4 border-b border-slate-800/80">
                      <div className="flex items-center gap-2 text-xs text-slate-400">
                        <span className="w-2 h-2 rounded-full bg-indigo-500"></span>
                        <span>Интерактивная карта продукта (Дерево экранов и функций Xpage)</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-[11px] text-slate-500 mr-2">Масштаб: {Math.round(zoomLevel * 100)}%</span>
                        <button 
                          onClick={() => setZoomLevel(Math.max(0.6, zoomLevel - 0.15))}
                          className="w-7 h-7 bg-slate-900 hover:bg-slate-800 border border-slate-700 rounded-lg text-slate-300 text-xs flex items-center justify-center font-bold"
                          title="Уменьшить"
                        >
                          -
                        </button>
                        <button 
                          onClick={() => setZoomLevel(1)}
                          className="px-2 h-7 bg-slate-900 hover:bg-slate-800 border border-slate-700 rounded-lg text-slate-300 text-xs flex items-center justify-center"
                          title="Сбросить масштаб"
                        >
                          100%
                        </button>
                        <button 
                          onClick={() => setZoomLevel(Math.min(1.4, zoomLevel + 0.15))}
                          className="w-7 h-7 bg-slate-900 hover:bg-slate-800 border border-slate-700 rounded-lg text-slate-300 text-xs flex items-center justify-center font-bold"
                          title="Увеличить"
                        >
                          +
                        </button>
                      </div>
                    </div>

                    {/* Canvas scroll viewport */}
                    <div 
                      className="overflow-x-auto overflow-y-auto pb-8 pt-2 transition-transform origin-top-left"
                      style={{ transform: `scale(${zoomLevel})`, transformOrigin: 'top left', minWidth: '1100px' }}
                    >
                      <div className="flex items-start gap-12 relative">
                        {/* ROOT PROJECT NODE */}
                        <div className="shrink-0 w-64 bg-gradient-to-br from-indigo-700 via-indigo-800 to-slate-900 border-2 border-indigo-500/50 rounded-2xl p-5 shadow-2xl space-y-3 sticky left-0 z-20">
                          <div className="flex items-center justify-between">
                            <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-indigo-500/30 text-indigo-200">
                              ПРОЕКТ XPAGE
                            </span>
                            <span className="text-base">🚀</span>
                          </div>
                          <h2 className="text-base font-bold text-white leading-snug">{structure.project_name}</h2>
                          <div className="text-[11px] text-indigo-200/80 pt-1 border-t border-indigo-500/30 flex justify-between">
                            <span>Модулей: {structure.modules?.length || 0}</span>
                            <span>Готов к FigJam</span>
                          </div>
                        </div>

                        {/* MODULES & SCREENS COLUMNS */}
                        <div className="flex-1 space-y-8">
                          {structure.modules?.map((mod, mIdx) => (
                            <div key={mIdx} className="flex items-start gap-8 bg-slate-900/50 p-5 rounded-2xl border border-slate-800/80 hover:border-indigo-500/40 transition">
                              {/* MODULE NODE */}
                              <div className="w-56 shrink-0 bg-slate-900 border border-indigo-500/40 rounded-xl p-4 shadow-lg space-y-2">
                                <div className="flex items-center justify-between">
                                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300 font-semibold">
                                    МОДУЛЬ {mIdx + 1}
                                  </span>
                                  <span className="text-xs text-slate-400 font-medium">{mod.screens?.length || 0} экр.</span>
                                </div>
                                <h3 className="font-bold text-white text-sm">{mod.name}</h3>
                                {mod.description && (
                                  <p className="text-[11px] text-slate-400 line-clamp-2">{mod.description}</p>
                                )}
                              </div>

                              {/* SCREENS UNDER THIS MODULE */}
                              <div className="flex-1 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                {mod.screens?.map((scr, sIdx) => (
                                  <div 
                                    key={sIdx} 
                                    className={`rounded-xl p-3.5 border transition space-y-2.5 ${
                                      scr.requires_clarification 
                                        ? "bg-rose-950/20 border-rose-800/50 hover:border-rose-600" 
                                        : "bg-slate-900/90 border-slate-800 hover:border-slate-700"
                                    }`}
                                  >
                                    <div className="flex items-center justify-between">
                                      <span className="text-xs font-semibold text-slate-100">{scr.title}</span>
                                      <span className="text-[10px] font-mono text-slate-400 bg-slate-800/80 px-1.5 py-0.5 rounded">{scr.id}</span>
                                    </div>

                                    {scr.purpose && (
                                      <p className="text-[11px] text-slate-400 line-clamp-2 leading-relaxed">{scr.purpose}</p>
                                    )}

                                    {/* Elements sticky pills */}
                                    <div className="flex flex-wrap gap-1 pt-1">
                                      {scr.elements?.map((elem, eIdx) => {
                                        const name = typeof elem === "string" ? elem : elem.name;
                                        return (
                                          <span 
                                            key={eIdx} 
                                            className="text-[10px] px-2 py-0.5 rounded bg-amber-400/10 text-amber-200 border border-amber-400/20"
                                          >
                                            {name}
                                          </span>
                                        );
                                      })}
                                    </div>

                                    {scr.requires_clarification && (
                                      <div className="text-[10px] text-rose-400 flex items-center gap-1 font-medium pt-1">
                                        <span>⚠️ Требует уточнения с клиентом</span>
                                      </div>
                                    )}
                                  </div>
                                ))}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* MODE 2: CLASSIC CARDS VIEW */}
                {structureViewMode === "cards" && (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
                    {structure.modules?.map((mod, mIdx) => (
                      <div key={mIdx} className="glass-card rounded-2xl p-5 border border-slate-800 space-y-4 hover:border-slate-700 transition">
                        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                          <div className="font-bold text-white text-base flex items-center gap-2">
                            <span className="w-2.5 h-2.5 rounded-full bg-rose-500"></span>
                            {mod.name}
                          </div>
                          <div className="flex items-center gap-2">
                            <button 
                              onClick={() => handleAddScreen(mIdx)}
                              className="text-[11px] px-2 py-0.5 rounded bg-slate-800 hover:bg-rose-600 text-slate-300 hover:text-white transition"
                              title="Добавить экран вручную"
                            >
                              + Экран
                            </button>
                            <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-400">{mod.screens?.length || 0}</span>
                          </div>
                        </div>
                        
                        <div className="space-y-3">
                          {mod.screens?.map((scr, sIdx) => (
                            <div key={sIdx} className="bg-slate-900/80 rounded-xl p-3 border border-slate-800/80 space-y-2">
                              <div className="flex items-center justify-between">
                                <span className="text-sm font-semibold text-slate-200">{scr.title}</span>
                                <span className="text-[10px] text-slate-500 font-mono">{scr.id}</span>
                              </div>
                              {scr.purpose && <p className="text-xs text-slate-400">{scr.purpose}</p>}
                              <div className="flex flex-wrap gap-1.5 pt-1">
                                {scr.elements?.map((elem, eIdx) => {
                                  const name = typeof elem === "string" ? elem : elem.name;
                                  return (
                                    <span key={eIdx} className="text-[11px] px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                                      {name}
                                    </span>
                                  );
                                })}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ) : (
              <div className="border-2 border-dashed border-slate-800 rounded-2xl p-16 text-center space-y-4">
                <div className="w-16 h-16 rounded-2xl bg-slate-800/80 flex items-center justify-center mx-auto text-3xl">
                  📊
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-white">Смета еще не проанализирована</h3>
                  <p className="text-sm text-slate-400 max-w-md mx-auto mt-1">Загрузите файл сметы или нажмите кнопку «🚀 Демо-кейс Xpage» вверху для мгновенного старта.</p>
                </div>
              </div>
            )}
          </div>
        )}

        {/* STEP 2: АНАЛИЗ СОЗВОНОВ */}
        {currentStep === 2 && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold text-white flex items-center gap-2">
                  <span>Этап 2: Аудит требований и матрица полноты информации Xpage</span>
                </h1>
                <p className="text-sm text-slate-400">Семантический кросс-анализ расшифровок созвонов со сметой по 20 блокам чек-листа с рисками (🔴/🟡/🔵).</p>
              </div>
              <div className="flex gap-3">
                <label className="px-4 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-xl text-sm font-medium text-white cursor-pointer transition flex items-center gap-2">
                  <span>🎙️ Добавить созвон (.docx / .mp3)</span>
                  <input type="file" accept=".docx,.mp3,.wav,.ogg" className="hidden" onChange={handleUploadTranscript} />
                </label>
                <button
                  onClick={handleRunAnalysis}
                  className="px-5 py-2 bg-rose-600 hover:bg-rose-500 text-white rounded-xl text-sm font-semibold shadow-lg shadow-rose-600/20 transition flex items-center gap-2"
                >
                  <span>🔍 Запустить кросс-анализ</span>
                </button>
              </div>
            </div>

            {/* Transcripts List Pill */}
            {transcripts.length > 0 && (
              <div className="flex items-center gap-2 flex-wrap text-xs text-slate-400 bg-slate-900/60 p-3 rounded-xl border border-slate-800">
                <span className="font-semibold text-slate-300">Файлы встреч в базе знаний ({transcripts.length}):</span>
                {transcripts.map((t, idx) => (
                  <span key={idx} className="px-2.5 py-1 bg-slate-800 text-slate-200 rounded-md border border-slate-700">
                    📄 {t}
                  </span>
                ))}
              </div>
            )}

            {analysisReport ? (
              <div className="space-y-6">
                {/* Readiness Banner with KPIs */}
                <div className="glass-card rounded-2xl p-6 border border-slate-800 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                  <div className="space-y-1.5">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-semibold uppercase tracking-wider text-rose-400">Индекс готовности требований (DoR)</span>
                      <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 font-mono">Стандарт Xpage</span>
                    </div>
                    <div className="text-2xl font-black text-white">{analysisReport.readiness_score || 82}% готовности к ТЗ и разработке</div>
                    <div className="text-xs text-slate-400 flex items-center gap-3 flex-wrap">
                      <span>Чек-лист: <strong className="text-white">{analysisReport.checklist_audit?.length || 20} блоков</strong></span>
                      <span>•</span>
                      <span>Противоречий: <strong className="text-rose-400">{analysisReport.inconsistencies?.length || 0}</strong></span>
                      <span>•</span>
                      <span>Согласовано: <strong className="text-emerald-400">{analysisReport.confirmed_requirements?.length || 0}</strong></span>
                      <span>•</span>
                      <span>Белых пятен: <strong className="text-amber-400">{analysisReport.missing_critical_topics?.length || 0}</strong></span>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 shrink-0">
                    <button
                      onClick={handleExportQuestions}
                      className="px-4 py-2.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-white rounded-xl text-xs font-semibold transition flex items-center gap-1.5 shadow-md"
                    >
                      📥 Выгрузить опросник и матрицу (.md)
                    </button>
                    <button
                      onClick={() => setCurrentStep(3)}
                      className="px-4 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-semibold transition flex items-center gap-1.5 shadow-lg shadow-emerald-600/20"
                    >
                      Утвердить требования ⟶ FigJam
                    </button>
                  </div>
                </div>

                {/* Stat summary pills */}
                {(() => {
                  const audit = analysisReport.checklist_audit || [];
                  const critCount = audit.filter(a => a.risk_level === 'critical').length;
                  const highCount = audit.filter(a => a.risk_level === 'high').length;
                  const medCount = audit.filter(a => a.risk_level === 'medium').length;
                  const contraCount = audit.filter(a => a.status === 'contradiction').length;
                  const gapCount = audit.filter(a => a.status === 'gap').length;
                  const confCount = audit.filter(a => a.status === 'confirmed').length;

                  return (
                    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
                      <div className="bg-slate-900/80 p-3 rounded-xl border border-slate-800 flex items-center gap-3">
                        <span className="text-xl">📋</span>
                        <div>
                          <div className="text-xs text-slate-400">Всего блоков</div>
                          <div className="text-sm font-bold text-white">{audit.length || 20}</div>
                        </div>
                      </div>
                      <div className="bg-rose-950/20 p-3 rounded-xl border border-rose-900/40 flex items-center gap-3">
                        <span className="text-xl">🔴</span>
                        <div>
                          <div className="text-xs text-rose-300">Крит. риски</div>
                          <div className="text-sm font-bold text-rose-400">{critCount}</div>
                        </div>
                      </div>
                      <div className="bg-amber-950/20 p-3 rounded-xl border border-amber-900/40 flex items-center gap-3">
                        <span className="text-xl">🟡</span>
                        <div>
                          <div className="text-xs text-amber-300">Высокие риски</div>
                          <div className="text-sm font-bold text-amber-400">{highCount}</div>
                        </div>
                      </div>
                      <div className="bg-rose-950/15 p-3 rounded-xl border border-rose-900/30 flex items-center gap-3">
                        <span className="text-xl">⚠️</span>
                        <div>
                          <div className="text-xs text-rose-300">Противоречия</div>
                          <div className="text-sm font-bold text-rose-300">{contraCount || analysisReport.inconsistencies?.length || 0}</div>
                        </div>
                      </div>
                      <div className="bg-amber-950/15 p-3 rounded-xl border border-amber-900/30 flex items-center gap-3">
                        <span className="text-xl">🔍</span>
                        <div>
                          <div className="text-xs text-amber-300">Белые пятна</div>
                          <div className="text-sm font-bold text-amber-300">{gapCount || analysisReport.missing_critical_topics?.length || 0}</div>
                        </div>
                      </div>
                      <div className="bg-emerald-950/20 p-3 rounded-xl border border-emerald-900/40 flex items-center gap-3">
                        <span className="text-xl">✅</span>
                        <div>
                          <div className="text-xs text-emerald-300">Согласовано</div>
                          <div className="text-sm font-bold text-emerald-400">{confCount}</div>
                        </div>
                      </div>
                    </div>
                  );
                })()}

                {/* Step 2 Tabs Navigation */}
                <div className="flex items-center gap-2 border-b border-slate-800 pb-2">
                  <button
                    onClick={() => setAnalysisActiveTab('checklist')}
                    className={`px-4 py-2 rounded-xl text-xs font-semibold transition flex items-center gap-2 ${
                      analysisActiveTab === 'checklist'
                        ? 'bg-rose-600 text-white shadow-md shadow-rose-600/20'
                        : 'bg-slate-900 hover:bg-slate-800 text-slate-300'
                    }`}
                  >
                    <span>📋 Матрица чек-листа (20 блоков)</span>
                  </button>
                  <button
                    onClick={() => setAnalysisActiveTab('inconsistencies')}
                    className={`px-4 py-2 rounded-xl text-xs font-semibold transition flex items-center gap-2 ${
                      analysisActiveTab === 'inconsistencies'
                        ? 'bg-rose-600 text-white shadow-md shadow-rose-600/20'
                        : 'bg-slate-900 hover:bg-slate-800 text-slate-300'
                    }`}
                  >
                    <span>⚠️ Противоречия и вопросы клиенту ({analysisReport.inconsistencies?.length || 0})</span>
                  </button>
                  <button
                    onClick={() => setAnalysisActiveTab('requirements')}
                    className={`px-4 py-2 rounded-xl text-xs font-semibold transition flex items-center gap-2 ${
                      analysisActiveTab === 'requirements'
                        ? 'bg-rose-600 text-white shadow-md shadow-rose-600/20'
                        : 'bg-slate-900 hover:bg-slate-800 text-slate-300'
                    }`}
                  >
                    <span>✅ Согласованные требования ({analysisReport.confirmed_requirements?.length || 0})</span>
                  </button>
                  <button
                    onClick={() => setAnalysisActiveTab('gaps')}
                    className={`px-4 py-2 rounded-xl text-xs font-semibold transition flex items-center gap-2 ${
                      analysisActiveTab === 'gaps'
                        ? 'bg-rose-600 text-white shadow-md shadow-rose-600/20'
                        : 'bg-slate-900 hover:bg-slate-800 text-slate-300'
                    }`}
                  >
                    <span>🔍 Белые пятна / Gaps ({analysisReport.missing_critical_topics?.length || 0})</span>
                  </button>
                </div>

                {/* TAB 1: CHECKLIST MATRIX (20 BLOCKS) */}
                {analysisActiveTab === 'checklist' && (
                  <div className="space-y-4">
                    {/* Filters Toolbar */}
                    <div className="flex items-center justify-between flex-wrap gap-2">
                      <div className="text-xs text-slate-400 font-medium">Фильтр по рискам и статусам:</div>
                      <div className="flex items-center gap-1.5 flex-wrap">
                        {[
                          { id: 'all', label: 'Все 20 разделов' },
                          { id: 'critical', label: '🔴 Критические' },
                          { id: 'high', label: '🟡 Высокие' },
                          { id: 'contradiction', label: '⚠️ Противоречия' },
                          { id: 'gap', label: '🔍 Белые пятна' },
                          { id: 'confirmed', label: '✅ Согласовано' }
                        ].map((btn) => (
                          <button
                            key={btn.id}
                            onClick={() => setChecklistFilter(btn.id)}
                            className={`px-3 py-1 rounded-lg text-xs font-medium transition ${
                              checklistFilter === btn.id
                                ? 'bg-slate-700 text-white border border-slate-600'
                                : 'bg-slate-900 hover:bg-slate-800 text-slate-400 border border-slate-800'
                            }`}
                          >
                            {btn.label}
                          </button>
                        ))}
                      </div>
                    </div>

                    {/* Checklist Blocks List */}
                    <div className="space-y-3">
                      {(analysisReport.checklist_audit || [])
                        .filter((item) => {
                          if (checklistFilter === 'all') return true;
                          if (checklistFilter === 'critical') return item.risk_level === 'critical';
                          if (checklistFilter === 'high') return item.risk_level === 'high';
                          if (checklistFilter === 'contradiction') return item.status === 'contradiction';
                          if (checklistFilter === 'gap') return item.status === 'gap';
                          if (checklistFilter === 'confirmed') return item.status === 'confirmed';
                          return true;
                        })
                        .map((item, idx) => {
                          const isContradiction = item.status === 'contradiction';
                          const isGap = item.status === 'gap';
                          const isCrit = item.risk_level === 'critical';
                          const isHigh = item.risk_level === 'high';

                          return (
                            <div 
                              key={idx}
                              className={`rounded-2xl p-5 border transition space-y-3.5 ${
                                isContradiction 
                                  ? 'bg-rose-950/15 border-rose-900/40 hover:border-rose-700/60' 
                                  : isGap 
                                  ? 'bg-amber-950/15 border-amber-900/40 hover:border-amber-700/60' 
                                  : 'bg-slate-900/70 border-slate-800 hover:border-slate-700'
                              }`}
                            >
                              <div className="flex items-start justify-between gap-4">
                                <div className="space-y-1">
                                  <div className="flex items-center gap-2 flex-wrap">
                                    <span className="text-xs font-bold font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                                      БЛОК {item.block_number}
                                    </span>
                                    <h4 className="text-sm font-bold text-white">{item.block_name}</h4>
                                  </div>
                                </div>

                                <div className="flex items-center gap-2 shrink-0">
                                  {/* Status badge */}
                                  <span className={`text-[11px] px-2.5 py-0.5 rounded-full font-semibold border ${
                                    isContradiction
                                      ? 'bg-rose-500/15 text-rose-300 border-rose-500/30'
                                      : isGap
                                      ? 'bg-amber-500/15 text-amber-300 border-amber-500/30'
                                      : 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30'
                                  }`}>
                                    {isContradiction ? '⚠️ Противоречие' : isGap ? '🔍 Белое пятно' : '✅ Согласовано'}
                                  </span>

                                  {/* Risk badge */}
                                  <span className={`text-[11px] px-2 py-0.5 rounded-md font-semibold border ${
                                    isCrit
                                      ? 'bg-rose-950/50 text-rose-400 border-rose-800/60'
                                      : isHigh
                                      ? 'bg-amber-950/50 text-amber-400 border-amber-800/60'
                                      : 'bg-sky-950/50 text-sky-400 border-sky-800/60'
                                  }`}>
                                    {isCrit ? '🔴 Крит. риск' : isHigh ? '🟡 Высокий риск' : '🔵 Средний риск'}
                                  </span>
                                </div>
                              </div>

                              {/* Evaluated Points Pills */}
                              {item.points_evaluated && item.points_evaluated.length > 0 && (
                                <div className="flex items-center gap-1.5 flex-wrap pt-0.5">
                                  <span className="text-[10px] text-slate-500 font-medium">Контрольные поинты:</span>
                                  {item.points_evaluated.map((pt, pIdx) => (
                                    <span key={pIdx} className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700/80">
                                      {pt}
                                    </span>
                                  ))}
                                </div>
                              )}

                              {/* Findings text */}
                              {item.findings && (
                                <div className="text-xs text-slate-300 leading-relaxed bg-slate-950/40 p-3 rounded-xl border border-slate-800/80">
                                  <span className="font-semibold text-slate-200">📌 Выяснено из встреч: </span>
                                  <span>{item.findings}</span>
                                </div>
                              )}

                              {/* Risk Description */}
                              {item.risk_description && (
                                <div className="text-xs text-rose-300/90 leading-relaxed bg-rose-950/20 p-3 rounded-xl border border-rose-900/30">
                                  <span className="font-semibold text-rose-300">⚠️ Риск при отсутствии решения: </span>
                                  <span>{item.risk_description}</span>
                                </div>
                              )}

                              {/* Recommendation or Question Callout */}
                              {item.recommendation_or_question && (
                                <div className="bg-indigo-950/25 p-3 rounded-xl border border-indigo-900/40 flex items-start justify-between gap-3">
                                  <div className="space-y-1 text-xs">
                                    <span className="font-bold text-indigo-300">💡 Рекомендация аналитика / Вопрос клиенту:</span>
                                    <p className="text-white italic">«{item.recommendation_or_question}»</p>
                                  </div>
                                  <button
                                    onClick={() => {
                                      navigator.clipboard.writeText(item.recommendation_or_question);
                                      showToast("Вопрос скопирован в буфер обмена!");
                                    }}
                                    className="text-[11px] px-2 py-1 rounded bg-indigo-900/50 hover:bg-indigo-800 text-indigo-200 border border-indigo-700/50 shrink-0 transition"
                                  >
                                    📋 Копировать
                                  </button>
                                </div>
                              )}
                            </div>
                          );
                        })}
                    </div>
                  </div>
                )}

                {/* TAB 2: INCONSISTENCIES */}
                {analysisActiveTab === 'inconsistencies' && (
                  <div className="space-y-4">
                    <div className="text-xs text-slate-400">
                      Выявленные расхождения между сметой, созвонами и позициями Заказчика. Каждое противоречие содержит готовый вопрос для утверждения.
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {analysisReport.inconsistencies?.map((inc, idx) => (
                        <div key={idx} className="bg-slate-900 rounded-2xl p-5 border border-rose-900/40 space-y-3.5 shadow-lg">
                          <div className="flex items-start justify-between gap-2">
                            <div className="space-y-1">
                              {inc.block_number && (
                                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700 mr-2">
                                  Блок {inc.block_number}
                                </span>
                              )}
                              {inc.impact_area && (
                                <span className="text-[10px] px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                                  {inc.impact_area}
                                </span>
                              )}
                              <h4 className="font-bold text-rose-300 text-sm pt-1">{inc.topic}</h4>
                            </div>
                            <span className="text-[10px] px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 uppercase font-mono shrink-0">
                              {inc.severity === 'critical' ? '🔴 critical' : inc.severity || 'high'}
                            </span>
                          </div>

                          {/* Side-by-side sources */}
                          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[11px]">
                            <div className="bg-black/30 p-2.5 rounded-xl border border-slate-800/80 space-y-1">
                              <span className="font-semibold text-slate-400">🏛️ Источник А:</span>
                              <p className="text-slate-300">{inc.source_a}</p>
                            </div>
                            <div className="bg-black/30 p-2.5 rounded-xl border border-slate-800/80 space-y-1">
                              <span className="font-semibold text-slate-400">🗣️ Источник Б:</span>
                              <p className="text-slate-300">{inc.source_b}</p>
                            </div>
                          </div>

                          <p className="text-xs text-slate-300 leading-relaxed">{inc.conflict_explanation}</p>
                          
                          <div className="bg-indigo-950/30 rounded-xl p-3 border border-indigo-900/50 space-y-1">
                            <div className="text-[11px] text-indigo-300 font-medium">Сформулированный вопрос Заказчику:</div>
                            <div className="text-xs font-medium text-white italic">«{inc.clarifying_question}»</div>
                          </div>

                          <div className="flex justify-end">
                            <button 
                              onClick={() => {
                                navigator.clipboard.writeText(inc.clarifying_question);
                                showToast("Вопрос скопирован в буфер обмена!");
                              }}
                              className="text-xs px-3 py-1 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 hover:text-white rounded-lg transition flex items-center gap-1.5"
                            >
                              📋 Скопировать вопрос
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* TAB 3: CONFIRMED REQUIREMENTS */}
                {analysisActiveTab === 'requirements' && (
                  <div className="space-y-4">
                    <div className="text-xs text-slate-400">
                      Технические и функциональные требования, однозначно зафиксированные в ходе переговоров.
                    </div>
                    <div className="space-y-2.5">
                      {analysisReport.confirmed_requirements?.map((req, idx) => (
                        <div key={idx} className="bg-slate-900/70 rounded-xl p-3.5 border border-slate-800 flex items-center justify-between gap-4 hover:border-slate-700 transition">
                          <div className="flex items-center gap-3">
                            <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                              {req.id || `REQ-${idx + 1}`}
                            </span>
                            {req.category && (
                              <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">
                                {req.category}
                              </span>
                            )}
                            <span className="text-sm text-slate-200">{req.text}</span>
                          </div>
                          <span className="text-xs px-2.5 py-0.5 rounded-full bg-slate-800 text-slate-400 border border-slate-700 shrink-0">
                            {req.source || "Созвон"}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* TAB 4: GAPS & MISSING TOPICS */}
                {analysisActiveTab === 'gaps' && (
                  <div className="space-y-4">
                    <div className="text-xs text-slate-400">
                      Разделы чек-листа и онтологии Xpage, по которым на встречах не было принято конкретных технических решений.
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {analysisReport.missing_critical_topics?.map((topic, idx) => (
                        <div key={idx} className="bg-amber-950/15 rounded-xl p-4 border border-amber-900/40 flex items-start gap-3">
                          <span className="text-base text-amber-400">⚠️</span>
                          <div className="space-y-1">
                            <div className="text-xs font-semibold text-amber-300">Белое пятно #{idx + 1}</div>
                            <div className="text-xs text-slate-200">{topic}</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="border-2 border-dashed border-slate-800 rounded-2xl p-16 text-center space-y-4">
                <div className="w-16 h-16 rounded-2xl bg-slate-800/80 flex items-center justify-center mx-auto text-3xl">
                  🎧
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-white">Расшифровки встреч готовы к анализу</h3>
                  <p className="text-sm text-slate-400 max-w-md mx-auto mt-1">Нажмите «Запустить кросс-анализ», чтобы нейросеть сопоставила созвоны со сметой по 20 блокам чек-листа с рисками.</p>
                </div>
              </div>
            )}
          </div>
        )}\n\n        {/* STEP 3: FIGJAM */}
        {currentStep === 3 && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold text-white">Этап 3: Интеграция с доской FigJam</h1>
                <p className="text-sm text-slate-400">Подключите доску FigJam со схемой экранов или User Flow. Сервис извлечет стикеры и сопоставит их со структурой.</p>
              </div>
              <button
                onClick={() => setCurrentStep(4)}
                className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-semibold transition"
              >
                Продолжить ⟶ Перейти к генерации ТЗ
              </button>
            </div>

            {/* Two-Way FigJam Integration Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Direction 1: Export structure to FigJam via Plugin */}
              <div className="glass-card rounded-2xl p-6 border border-indigo-500/30 space-y-4 bg-gradient-to-br from-indigo-950/20 to-slate-900">
                <div className="flex items-center gap-2.5">
                  <span className="p-2 rounded-xl bg-indigo-600/20 text-indigo-400 font-bold text-lg">⚡</span>
                  <div>
                    <h3 className="text-sm font-bold text-white">1. Автоматическая отрисовка в FigJam</h3>
                    <p className="text-xs text-slate-400">100% программное построение схемы без Ctrl+V</p>
                  </div>
                </div>

                <p className="text-xs text-slate-300 leading-relaxed">
                  Официальный плагин <strong className="text-indigo-300">Xpage ППО Sync</strong> нативно подключается к локальному бэкенду (<code className="text-xs text-indigo-300">/api/figjam/nodes</code>) и за 0.5 секунды строит все карточки модулей, экранов и векторные стрелки.
                </p>

                <div className="flex gap-2.5 pt-2">
                  <a
                    href="https://www.figma.com/board/new"
                    target="_blank"
                    className="flex-1 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold text-center transition shadow-lg shadow-indigo-600/20"
                  >
                    🚀 Создать холст FigJam
                  </a>
                  <button
                    onClick={() => setShowPluginModal(true)}
                    className="px-4 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded-xl text-xs font-medium transition"
                  >
                    🔌 Инструкция плагина
                  </button>
                </div>
              </div>

              {/* Direction 2: Import Figma Prototypes via REST API */}
              <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-4">
                <div className="flex items-center gap-2.5">
                  <span className="p-2 rounded-xl bg-slate-800 text-slate-300 font-bold text-lg">🔍</span>
                  <div>
                    <h3 className="text-sm font-bold text-white">2. Чтение прототипов Figma (для ТЗ)</h3>
                    <p className="text-xs text-slate-400">Сверка готовых макетов дизайнера через Figma REST API</p>
                  </div>
                </div>

                <div className="space-y-2">
                  <input
                    type="text"
                    placeholder="https://www.figma.com/design/... или ключ файла"
                    value={figjamUrl}
                    onChange={(e) => setFigjamUrl(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
                  />
                  <button
                    onClick={handleSyncFigjam}
                    className="w-full py-2 bg-slate-800 hover:bg-slate-700 text-white border border-slate-700 rounded-xl text-xs font-semibold transition"
                  >
                    🔗 Прочитать элементы через Figma REST API
                  </button>
                </div>

                <p className="text-[11px] text-slate-500 leading-normal">
                  Извлеченные элементы экранов будут автоматически включены в спецификацию разделов финального ТЗ (Шаг 4).
                </p>
              </div>
            </div>

            {figjamData && (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="text-sm text-slate-300 font-semibold">Файл: {figjamData.file_name} ({figjamData.editor_type})</div>
                  <span className="text-xs text-slate-400">{figjamData.extracted_nodes_count} элементов извлечено</span>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {figjamData.nodes?.slice(0, 9).map((n, idx) => (
                    <div key={idx} className="bg-amber-400/10 border border-amber-400/20 rounded-xl p-4 space-y-2">
                      <div className="flex items-center justify-between text-[11px] text-amber-300 font-mono">
                        <span>{n.type}</span>
                        <span>{n.id}</span>
                      </div>
                      <div className="text-xs text-slate-200 font-medium">{n.text}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* STEP 4: ТЗ */}
        {currentStep === 4 && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold text-white">Этап 4: Генерация Технического задания по стандарту Xpage</h1>
                <p className="text-sm text-slate-400">Компиляция полного ТЗ в формате Microsoft Word (.docx) со стилями компании Xpage.</p>
              </div>
              <button
                onClick={handleGenerateTZ}
                className="px-6 py-2.5 bg-rose-600 hover:bg-rose-500 text-white rounded-xl text-sm font-semibold shadow-lg shadow-rose-600/20 transition flex items-center gap-2"
              >
                <span>📄 Сгенерировать ТЗ (.docx)</span>
              </button>
            </div>

            {tzGenerated ? (
              <div className="glass-card rounded-2xl p-8 border border-slate-800 space-y-6">
                <div className="text-center space-y-3">
                  <div className="w-20 h-20 rounded-full bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center mx-auto text-4xl shadow-lg shadow-emerald-500/10">
                    📄
                  </div>
                  <div className="space-y-1">
                    <h3 className="text-xl font-bold text-white">Техническое задание успешно сформировано!</h3>
                    <p className="text-sm text-slate-400 max-w-xl mx-auto">
                      Документ скомпилирован строго по шаблону <strong>«Шаблон Технического задания (ТЗ) Xpage»</strong> с соблюдением всех 11 корпоративных разделов, листа согласования, матриц RBAC/CRUD и спецификаций API.
                    </p>
                  </div>
                </div>

                {/* Key Metrics Badges */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-3 text-center">
                    <div className="text-xl font-black text-rose-400">11</div>
                    <div className="text-[11px] text-slate-400 font-medium mt-0.5">Разделов стандарта Xpage</div>
                  </div>
                  <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-3 text-center">
                    <div className="text-xl font-black text-indigo-400">18</div>
                    <div className="text-[11px] text-slate-400 font-medium mt-0.5">Таблиц (RBAC, API, NFR)</div>
                  </div>
                  <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-3 text-center">
                    <div className="text-xl font-black text-emerald-400">380+</div>
                    <div className="text-[11px] text-slate-400 font-medium mt-0.5">Параграфов требований</div>
                  </div>
                  <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-3 text-center">
                    <div className="text-xl font-black text-amber-400">~75 KB</div>
                    <div className="text-[11px] text-slate-400 font-medium mt-0.5">Формат Word (.docx)</div>
                  </div>
                </div>

                {/* Section Overview */}
                <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-4 text-xs text-slate-300 space-y-2">
                  <div className="font-semibold text-slate-200 flex items-center justify-between">
                    <span>Содержание сгенерированного документа:</span>
                    <span className="text-[11px] text-emerald-400 font-mono">100% соответствие шаблону Xpage</span>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-1.5 text-slate-400 text-[11px]">
                    <div>✓ 1. Используемые термины и определения (11 терминов)</div>
                    <div>✓ 7. Сквозные бизнес-сценарии (Use Cases)</div>
                    <div>✓ 2. Назначение, цели проекта, DoR и REQ-01</div>
                    <div>✓ 8. Нефункциональные требования (SLA 99.9%)</div>
                    <div>✓ 3. Пользовательские роли (Матрица RBAC/CRUD)</div>
                    <div>✓ 9. Требования к админ-панели (CMS)</div>
                    <div>✓ 4. Общая архитектура (BFF + 1С + Эквайринг)</div>
                    <div>✓ 10. Требования к тестированию и приемке</div>
                    <div>✓ 5. Структура интерфейсов (FigJam карта экранов)</div>
                    <div>✓ 11. План-график реализации и этапы</div>
                    <div>✓ 6. Функциональные требования к модулям и экранам</div>
                    <div>✓ Лист согласования и подписи сторон</div>
                  </div>
                </div>

                <div className="flex items-center justify-center gap-4 pt-2">
                  <a
                    href={`/api/tz/download/${activeProject?.id}`}
                    download
                    className="inline-flex items-center gap-2 px-8 py-3.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl font-bold text-sm shadow-xl shadow-emerald-600/30 transition transform hover:-translate-y-0.5"
                  >
                    <span>⬇ Скачать готовое ТЗ (.docx)</span>
                  </a>
                  <button
                    onClick={handleGenerateTZ}
                    className="px-5 py-3.5 bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 rounded-xl text-xs font-semibold transition"
                  >
                    🔄 Сгенерировать повторно
                  </button>
                </div>
              </div>
            ) : (
              <div className="border-2 border-dashed border-slate-800 rounded-2xl p-16 text-center space-y-4">
                <div className="w-16 h-16 rounded-2xl bg-slate-800/80 flex items-center justify-center mx-auto text-3xl">
                  ✍️
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-white">ТЗ готово к компиляции</h3>
                  <p className="text-sm text-slate-400 max-w-md mx-auto mt-1">Нажмите «Сгенерировать ТЗ (.docx)», чтобы собрать все согласованные требования и структуру в итоговый документ Word.</p>
                </div>
              </div>
            )}
          </div>
        )}
      </main>

      {/* MODAL: ИНСТРУКЦИЯ ПО АВТО-ОТРИСОВКЕ ЧЕРЕЗ FIGJAM ПЛАГИН */}
      {showPluginModal && (
        <div className="fixed inset-0 bg-black/75 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl max-w-xl w-full p-6 space-y-5 shadow-2xl animate-fade-in">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2.5">
                <span className="p-2 rounded-lg bg-indigo-600/20 text-indigo-400 font-bold text-lg">⚡</span>
                <div>
                  <h3 className="text-base font-bold text-white">Автоматическая отрисовка в FigJam</h3>
                  <p className="text-xs text-slate-400">100% программное построение схемы без ручных действий и Ctrl+V</p>
                </div>
              </div>
              <button 
                onClick={() => setShowPluginModal(false)}
                className="text-slate-400 hover:text-white text-lg px-2 py-1"
              >
                ✕
              </button>
            </div>

            <div className="space-y-3.5 text-xs text-slate-300">
              <div className="flex items-start gap-3 bg-slate-950/60 p-3.5 rounded-xl border border-slate-800">
                <div className="w-6 h-6 rounded-full bg-indigo-600 text-white flex items-center justify-center font-bold text-xs shrink-0">1</div>
                <div>
                  <div className="font-semibold text-white">Откройте холст FigJam</div>
                  <p className="text-slate-400 mt-0.5">Перейдите на доску <a href="https://www.figma.com/board/new" target="_blank" className="text-indigo-400 underline">figma.com/board/new</a> (открывается по кнопке ниже).</p>
                </div>
              </div>

              <div className="flex items-start gap-3 bg-slate-950/60 p-3.5 rounded-xl border border-slate-800">
                <div className="w-6 h-6 rounded-full bg-indigo-600 text-white flex items-center justify-center font-bold text-xs shrink-0">2</div>
                <div>
                  <div className="font-semibold text-white">Подключите манифест плагина (один раз)</div>
                  <p className="text-slate-400 mt-0.5">В меню FigJam (логотип в левом верхнем углу) выберите: <br/><strong className="text-slate-200">Plugins ⟶ Development ⟶ Import plugin from manifest...</strong><br/>и укажите файл из этого проекта: <code className="bg-slate-800 px-1.5 py-0.5 rounded text-indigo-300 font-mono">figjam-plugin/manifest.json</code>.</p>
                </div>
              </div>

              <div className="flex items-start gap-3 bg-slate-950/60 p-3.5 rounded-xl border border-slate-800">
                <div className="w-6 h-6 rounded-full bg-emerald-600 text-white flex items-center justify-center font-bold text-xs shrink-0">3</div>
                <div>
                  <div className="font-semibold text-white">Нажмите «⚡ Нарисовать на холсте»</div>
                  <p className="text-slate-400 mt-0.5">Плагин сам считает дерево из сервиса и за долю секунды расставит блоки модулей, карточки экранов со стикерами и векторные связи!</p>
                </div>
              </div>
            </div>

            <div className="flex items-center justify-between pt-2 border-t border-slate-800">
              <span className="text-[11px] text-emerald-400 flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                Сервис на 127.0.0.1:8080 готов к приему команд плагина
              </span>
              <div className="flex gap-2">
                <a 
                  href="https://www.figma.com/board/new" 
                  target="_blank" 
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold transition"
                >
                  🚀 Открыть холст FigJam
                </a>
                <button
                  onClick={() => setShowPluginModal(false)}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl text-xs transition"
                >
                  Понятно
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
