/** @OnlyCurrentDoc */

function onEdit() {
  ss = SpreadsheetApp.getActiveSpreadsheet()
  r = ss.getActiveRange()
  openEndedNamedRange = [["mainDB", "Database"], ["metrics", "Metrics"]]
  ssDatabase = ss.getSheetByName("Database")
  ssEfficiency = ss.getSheetByName("Efficiency-Calculator")
  dbLock = ssDatabase.getRange("H5")
  dbAddButton = ssDatabase.getRange("H2")
  dbUpdEffButton = ssDatabase.getRange("I2")

  //*******************//
  // Fixed Named Range //
  //*******************//
  efficiencyTable = ss.getRangeByName("efficiencyTable").getValues()
  members = ss.getRangeByName("members").getValues()

  //**********//
  //   main   //
  //**********//
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
  Logger.log(arrayRangeNameAndSheet)
  var rangeName = arrayRangeNameAndSheet[0]
  Logger.log(rangeName)
  var sheetName = arrayRangeNameAndSheet[1]
  var _range = ss.getRangeByName(rangeName)
  var _sheet = ss.getSheetByName(sheetName)
  var rangeA1Notation = _range.getA1Notation()
  Logger.log(rangeA1Notation)
  var rangeAddress = rangeA1Notation.split(":")
  var rangeStart = rangeAddress[0]
  var rangeEnd = rangeAddress[1]
  var rangeLastCol = rangeEnd.substring(0,1)
  var sheetLastRow = _sheet.getLastRow()
  var newRangeA1Notation = rangeStart+":"+rangeLastCol+sheetLastRow
  Logger.log(newRangeA1Notation)
  var newRange = _sheet.getRange(newRangeA1Notation)

  if (rangeA1Notation == newRangeA1Notation) {
    return 0
  } else {
    ss.removeNamedRange(rangeName)
    ss.setNamedRange(rangeName, newRange)
  }
}

function addData() {
  // refresh named range in case there are any updates
  updOpenEndedNamedRange(["metrics", "Metrics"])
  updOpenEndedNamedRange(["mainDB", "Database"])

  var members = ss.getRangeByName("members").getValues()
  var metrics = ss.getRangeByName("metrics").getValues()
  var date = ss.getRangeByName("mainDBDate").getValue()
  // var date = Utilities.formatDate(new Date(), "GMT", "dd/MM/yyyy")

  var output = []
  for (var x=0; x<members.length; x++) {
    for (var y=0; y<metrics.length; y++) {
      output.push([members[x], metrics[y], date, null])
    }
  }

  // define the range where the output should be written to
  var dbLastRow = ssDatabase.getLastRow()
  var outputRowCount = members.length * metrics.length
  var outputRange = ssDatabase.getRange("R"+(dbLastRow+1)+"C1:R"+(dbLastRow+outputRowCount)+"C4")

  // write data to database
  Logger.log(output)
  outputRange.setValues(output)

  // update named range
  updOpenEndedNamedRange(["mainDB", "Database"])

  // sort database
  ss.getRangeByName("mainDB").sort([{column: 3, ascending: false}, {column: 1}, {column: 2}])

  // find new last row and apply concatenate formula
  var newLastRow = ss.getRangeByName("mainDB").getLastRow()
  var formulaRange = ssDatabase.getRange("R2C5:R"+newLastRow+"C5")
  formulaRange.setFormula("=CONCATENATE(A2,B2,C2)")

  // reset checkbox to false
  dbAddButton.setValue("false")
  dbLock.setValue("true")
}

function updateEfficiency() {
  updOpenEndedNamedRange(["mainDB", "Database"])
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

  var dbLastRow = ssDatabase.getLastRow()
  Logger.log(dbLastRow)
  var outputRange = ssDatabase.getRange("R"+(dbLastRow+1)+"C1:R"+(dbLastRow+output.length)+"C4")
  Logger.log(outputRange.getA1Notation())
  outputRange.setValues(output)

  // update named range
  updOpenEndedNamedRange(["mainDB", "Database"])

  // re-calculate last row
  var newLastRow = ss.getRangeByName("mainDB").getLastRow()

  // sort database
  ss.getRangeByName("mainDB").sort([{column: 3, ascending: false}, {column: 1}, {column: 2}])

  // add formula to generate primary key for lookup
  var formulaRange = ssDatabase.getRange("R2C5:R"+newLastRow+"C5")
  formulaRange.setFormula("=CONCATENATE(A2,B2,C2)")

  // reset checkbox to false
  dbUpdEffButton.setValue("false")
  dbLock.setValue("true")
}
