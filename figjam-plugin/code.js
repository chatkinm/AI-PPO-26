// Xpage ППО FigJam Sync Plugin Engine
const BACKEND_URL = 'http://localhost:8080';

figma.showUI(__html__, { width: 340, height: 420, themeColors: true });

async function drawStructure(payload) {
  const { nodes, connectors } = payload;

  try {
    // 1. Предзагрузка шрифтов Inter
    await figma.loadFontAsync({ family: "Inter", style: "Medium" });
    await figma.loadFontAsync({ family: "Inter", style: "Bold" });
    await figma.loadFontAsync({ family: "Inter", style: "Regular" });

    const createdNodes = {};
    const allCreated = [];

    // 2. Создание узлов на холсте FigJam
    for (const n of nodes) {
      const shape = figma.createShapeWithText();
      shape.shapeType = 'ROUNDED_RECTANGLE';
      shape.x = n.x;
      shape.y = n.y;
      shape.resize(n.width, n.height);

      // Цвета заливки (Fills)
      if (n.fill_color) {
        shape.fills = [{
          type: 'SOLID',
          color: { r: n.fill_color.r, g: n.fill_color.g, b: n.fill_color.b }
        }];
      }

      // Стилизация границ (Strokes)
      if (n.stroke_color) {
        shape.strokes = [{
          type: 'SOLID',
          color: { r: n.stroke_color.r, g: n.stroke_color.g, b: n.stroke_color.b }
        }];
        shape.strokeWeight = 1;
      } else {
        shape.strokes = [];
      }

      // Текст узла (устанавливаем сначала characters, затем стилизацию)
      const fullText = n.title + (n.subtitle ? '\n' + n.subtitle : '');
      shape.text.characters = fullText;

      // Начертание шрифта (Regular / Medium / Bold)
      let fontStyle = "Regular";
      if (n.font_weight === 'Bold') {
        fontStyle = "Bold";
      } else if (n.font_weight === 'Medium') {
        fontStyle = "Medium";
      }
      try {
        shape.text.fontName = { family: "Inter", style: fontStyle };
      } catch (e) {
        // шрифт по умолчанию
      }

      // Цвет текста
      if (n.text_color) {
        try {
          shape.text.fills = [{
            type: 'SOLID',
            color: { r: n.text_color.r, g: n.text_color.g, b: n.text_color.b }
          }];
        } catch (e) {}
      }

      // Выравнивание текста (блочные элементы - влево, шапки - по центру)
      try {
        if (n.type === 'BLOCK') {
          shape.text.textAlignHorizontal = 'LEFT';
        } else {
          shape.text.textAlignHorizontal = 'CENTER';
        }
      } catch (e) {}

      createdNodes[n.id] = shape;
      allCreated.push(shape);
    }

    // 3. Создание связей (Connectors)
    for (const conn of connectors) {
      const start = createdNodes[conn.start_id];
      const end = createdNodes[conn.end_id];

      if (start && end) {
        const connector = figma.createConnector();
        const startMagnet = conn.start_magnet || "AUTO";
        const endMagnet = conn.end_magnet || "AUTO";
        connector.connectorStart = { endpointNodeId: start.id, magnet: startMagnet };
        connector.connectorEnd = { endpointNodeId: end.id, magnet: endMagnet };
        connector.connectorLineType = "ELBOWED";

        if (conn.stroke_color) {
          connector.strokes = [{
            type: 'SOLID',
            color: { r: conn.stroke_color.r, g: conn.stroke_color.g, b: conn.stroke_color.b }
          }];
          connector.strokeWeight = 1.5;
        }
        allCreated.push(connector);
      }
    }

    // 4. Центрирование камеры на всей созданной структуре
    if (allCreated.length > 0) {
      figma.currentPage.selection = allCreated;
      figma.viewport.scrollAndZoomIntoView(allCreated);
    }

    figma.notify("✨ Архитектура экранов Xpage успешно построена на холсте!");
    figma.ui.postMessage({ type: 'DRAW_DONE' });

  } catch (err) {
    figma.notify("Ошибка создания: " + err.message, { error: true });
    figma.ui.postMessage({ type: 'DRAW_ERROR', error: err.message });
  }
}

figma.ui.onmessage = async (msg) => {
  if (msg.type === 'FETCH_PROJECTS') {
    try {
      const resp = await fetch(BACKEND_URL + '/api/figjam/projects');
      const data = await resp.json();
      figma.ui.postMessage({ type: 'PROJECTS_LOADED', projects: data });
    } catch (e) {
      figma.ui.postMessage({ type: 'FETCH_ERROR', error: e.message });
    }
  } else if (msg.type === 'FETCH_AND_DRAW') {
    try {
      figma.notify("⏳ Загрузка структуры и расчет связей...");
      const resp = await fetch(BACKEND_URL + '/api/figjam/nodes/' + msg.projectId);
      const payload = await resp.json();
      await drawStructure(payload);
    } catch (e) {
      figma.notify("Ошибка загрузки данных: " + e.message, { error: true });
      figma.ui.postMessage({ type: 'DRAW_ERROR', error: e.message });
    }
  } else if (msg.type === 'DRAW_STRUCTURE') {
    await drawStructure(msg.payload);
  }
};
