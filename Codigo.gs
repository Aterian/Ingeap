function doGet(e) {
  // Manejar el caso donde no hay parámetros (p. ej. cuando abren la URL directamente en el navegador)
  if (!e || !e.parameter || !e.parameter.action) {
    return ContentService.createTextOutput(JSON.stringify({error: "Falta el parámetro action"}))
      .setMimeType(ContentService.MimeType.JSON);
  }

  var action = e.parameter.action;
  var ss = SpreadsheetApp.getActiveSpreadsheet(); // Si el script está adjunto al Sheet
  // var ss = SpreadsheetApp.openById('TU_ID_DE_SPREADSHEET'); // Si el script es independiente

  // ------------- PANTALLA 1: LOGIN -------------
  if (action === 'login') {
    var email = e.parameter.email;
    var clave = e.parameter.clave;
    var sheet = ss.getSheetByName('Usuarios');
    
    if (!sheet) return ContentService.createTextOutput(JSON.stringify({success: false, message: "Hoja 'Usuarios' no encontrada"})).setMimeType(ContentService.MimeType.JSON);
    
    var data = sheet.getDataRange().getValues();
    
    // Columnas esperadas: Nombre (0), Email (1), Clave (2), Area (3)
    for (var i = 1; i < data.length; i++) {
      if (data[i][1] === email && data[i][2] === clave) {
        return ContentService.createTextOutput(JSON.stringify({
          success: true,
          nombre: data[i][0],
          area: data[i][3]
        })).setMimeType(ContentService.MimeType.JSON);
      }
    }
    
    return ContentService.createTextOutput(JSON.stringify({
      success: false,
      message: "Credenciales inválidas"
    })).setMimeType(ContentService.MimeType.JSON);
  }

  // ------------- PANTALLA 2: GET PROYECTOS -------------
  if (action === 'get_projects') {
    var area = e.parameter.area;
    var sheet = ss.getSheetByName('Proyectos');
    
    if (!sheet) return ContentService.createTextOutput(JSON.stringify({success: false, message: "Hoja 'Proyectos' no encontrada"})).setMimeType(ContentService.MimeType.JSON);
    
    var data = sheet.getDataRange().getValues();
    var projects = [];
    
    // Columnas esperadas: Codigo_Proyecto (0), Area (1), Estado (2)
    for (var i = 1; i < data.length; i++) {
      var p_codigo = data[i][0];
      var p_area = data[i][1];
      var p_estado = data[i][2];
      
      if (p_area === area && p_estado !== 'Rechazado' && p_estado !== 'Archivado') {
        projects.push(p_codigo);
      }
    }
    
    return ContentService.createTextOutput(JSON.stringify({
      success: true,
      projects: projects
    })).setMimeType(ContentService.MimeType.JSON);
  }

  // ------------- PANTALLA 3: GET CHAT LOG -------------
  if (action === 'get_chat') {
    var id_proyecto = e.parameter.id_proyecto;
    var sheet = ss.getSheetByName('Chat_Log');
    
    if (!sheet) return ContentService.createTextOutput(JSON.stringify({success: false, message: "Hoja 'Chat_Log' no encontrada"})).setMimeType(ContentService.MimeType.JSON);
    
    var data = sheet.getDataRange().getValues();
    var messages = [];
    
    // Columnas esperadas: ID_Proyecto (0), Area (1), Usuario_Nombre (2), Usuario_Email (3), Mensaje (4), Fecha (5), Hora (6)
    for (var i = 1; i < data.length; i++) {
      if (data[i][0] === id_proyecto) {
        messages.push({
          usuario: data[i][2],
          mensaje: data[i][4],
          // Si es un objeto Date de Google Sheets, lo formateamos a string:
          fecha: (data[i][5] instanceof Date) ? Utilities.formatDate(data[i][5], Session.getScriptTimeZone(), "yyyy-MM-dd") : data[i][5],
          hora: (data[i][6] instanceof Date) ? Utilities.formatDate(data[i][6], Session.getScriptTimeZone(), "HH:mm:ss") : data[i][6]
        });
      }
    }
    
    return ContentService.createTextOutput(JSON.stringify({
      success: true,
      messages: messages
    })).setMimeType(ContentService.MimeType.JSON);
  }

  return ContentService.createTextOutput(JSON.stringify({error: "Acción no reconocida"}))
    .setMimeType(ContentService.MimeType.JSON);
}

// ------------- PANTALLA 3: POST MENSAJE -------------
function doPost(e) {
  try {
    // Si la data viene en el body crudo como JSON
    var data = JSON.parse(e.postData.contents);
    var ss = SpreadsheetApp.getActiveSpreadsheet(); 
    var sheet = ss.getSheetByName('Chat_Log');
    
    if (!sheet) throw new Error("Hoja 'Chat_Log' no encontrada");
    
    // Columnas: ID_Proyecto, Area, Usuario_Nombre, Usuario_Email, Mensaje, Fecha, Hora
    sheet.appendRow([
      data.ID_Proyecto,
      data.Area,
      data.Nombre_Usuario,
      data.Email,
      data.Mensaje,
      data.Fecha,
      data.Hora
    ]);
    
    return ContentService.createTextOutput(JSON.stringify({success: true}))
      .setMimeType(ContentService.MimeType.JSON);
      
  } catch (error) {
    return ContentService.createTextOutput(JSON.stringify({
      success: false, 
      error: error.toString()
    })).setMimeType(ContentService.MimeType.JSON);
  }
}
