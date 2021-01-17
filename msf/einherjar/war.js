/** @OnlyCurrentDoc */

function onEdit() {
  ss = SpreadsheetApp.getActiveSpreadsheet()
  r = ss.getActiveRange()
  openEndedNamedRange = [["mainDB", "Database"], ["metrics", "Metrics"]]
  ssDatabase = ss.getSheetByName("Database")
  ssEfficiency = ss.getSheetByName("Efficiency-Calculator")
  ssMembers = ss.getSheetByName("Members")
  ssMetrics = ss.getSheetByName("Metrics")
  dbLock = ssDatabase.getRange("H5")
  dbAddButton = ssDatabase.getRange("H2")
  dbUpdEffButton = ssDatabase.getRange("I2")

  //*******************//
  // Fixed Named Range //
  //*******************//
  efficiencyTable = ss.getRangeByName("efficiencyTable").getValues()
  members = ss.getRangeByName("members").getValues()

  //************************//
  // Open Ended Named Range //
  //************************//
  mainDB = ss.getRangeByName("mainDB").getValues()
  metrics = ss.getRangeByName("metrics").getValues()

  if (dbLock.getValue() == true) {
    Logger.log("sheet is locked")
    return 0
  } else if (r.getRow() == dbAddButton.getRow() && r.getColumn() == dbAddButton.getColumn() && dbAddButton.getValue() == true) {
    Logger.log("executing addData()")
    addData()
  } else if (r.getRow() == dbUpdEffButton.getRow() && r.getColumn() == dbUpdEffButton.getColumn() && dbUpdEffButton.getValue() == true) {
    Logger.log("executing updateEfficiency()")
    updateEfficiency()
  }
}

function updOpenEndedNamedRange(arrayRangeNameAndSheet) {
  for (i in arrayRangeNameAndSheet) {
    var rangeName = arrayRangeNameAndSheet[i][0]
    var sheetName = arrayRangeNameAndSheet[i][1]
    var _range = ss.getRangeByName(rangeName)
    var _sheet = ss.getSheetByName(sheetName)
    var rangeA1Notation = _range.getA1Notation()
    var rangeAddress = rangeA1Notation.split(":")
    var rangeStart = rangeAddress[0]
    var rangeEnd = rangeAddress[1]
    var rangeLastCol = rangeEnd.substring(0,1)
    var sheetLastRow = _sheet.getLastRow()
    var newRangeA1Notation = rangeStart+":"+rangeLastCol+sheetLastRow
    var newRange = _sheet.getRange(newRangeA1Notation)
    ss.removeNamedRange(rangeName)
    ss.setNamedRange(rangeName, newRange)
  }
}

function addData() {
  var dbLastRow = ssDatabase.getLastRow()
  var members = getMembers()
  var metrics = getMetrics()
  var date = ssDatabase.getRange("G2").getValue()
  // var date = Utilities.formatDate(new Date(), "GMT", "dd/MM/yyyy")

  var output = []
  for (var x=0; x<members.length; x++) {
    for (var y=0; y<metrics.length; y++) {
      output.push([members[x], metrics[y], date, null])
    }
  }
  var outputRowCount = members.length * metrics.length
  var outputRange = ssDatabase.getRange("R"+(dbLastRow+1)+"C1:R"+(dbLastRow+outputRowCount)+"C4")
  Logger.log(output)
  outputRange.setValues(output)

  var newLastRow = ssDatabase.getLastRow()
  var dataRange = ssDatabase.getRange("R2C1:R"+newLastRow+"C4")
  dataRange.sort([{column: 3, ascending: false}, {column: 1}, {column: 2}])

  var formulaRange = ssDatabase.getRange("R2C5:R"+newLastRow+"C5")
  formulaRange.setFormula("=CONCATENATE(A2,B2,C2)")

  // reset checkbox to false
  dbAddButton.setValue("false")
  dbLock.setValue("true")
}

// function getMembers() {
//   var membersLastRow = ssMembers.getLastRow()
//   Logger.log("last row: "+membersLastRow)
//   var members = ssMembers.getRange("A1:A"+membersLastRow)
//   // Logger.log(members.getValues())
//   return members.getValues()
// }

// function getMetrics() {
//   var metricsLastRow = ssMetrics.getLastRow()
//   Logger.log("last row: "+metricsLastRow)
//   var metrics = ssMetrics.getRange("A1:A"+metricsLastRow)
//   // Logger.log(metrics.getValues())
//   return metrics.getValues()
// }

function updateEfficiency() {
  // var effDataSet = ssEfficiency.getRange("E3:I26").getValues()
  // var effDataSet = ssEfficiency.getRangeByName("EfficiencyTable").getValues()
  // var dataDate = ssEfficiency.getRange("E2").getValue()
  // var lastRow = ssDatabase.getLastRow()
  // var dbDataSet = ssDatabase.getRange("R2C1:R"+lastRow+"C5").getValues()
  var dataDate = ss.getRangeByName("efficiencyTableDate").getValue()
  Logger.log(efficiencyTable)
  Logger.log(dataDate)

  output = []
  efficiencyTable.forEach(
    function(row) {
      output.push([row[0], "Failed Attacks", dataDate, row[2]])
      output.push([row[0], "Efficiency", dataDate, row[4]])
    }
  )
  Logger.log(output)
  Logger.log(output.length)

  Logger.log(lastRow)
  var outputRange = ssDatabase.getRange("R"+(lastRow+1)+"C1:R"+(lastRow+output.length)+"C4")
  Logger.log(outputRange.getA1Notation())
  outputRange.setValues(output)

  // update named range
  updOpenEndedNamedRange(["mainDB", "Database"])

  // re-calculate last row
  var newLastRow = ssDatabase.getLastRow()

  // sort database
  // var dataRange = ssDatabase.getRange("R2C1:R"+newLastRow+"C4")
  // dataRange.sort([{column: 3, ascending: false}, {column: 1}, {column: 2}])
  ss.getRangeByName("mainDB").sort([{column: 3, ascending: false}, {column: 1}, {column: 2}])

  // add formula to generate primary key for lookup
  var formulaRange = ssDatabase.getRange("R2C5:R"+newLastRow+"C5")
  formulaRange.setFormula("=CONCATENATE(A2,B2,C2)")

  // reset checkbox to false
  dbUpdEffButton.setValue("false")
  dbLock.setValue("true")
}
