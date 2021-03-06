/** @OnlyCurrentDoc */

function onEdit() {
  ss = SpreadsheetApp.getActiveSpreadsheet()
  r = ss.getActiveRange()
  openEndedNamedRange = [["mainDB", "Database"], ["metrics", "Metrics"], ["failedAttacksDB", "Failed-Attacks"]]
  ssDatabase = ss.getSheetByName("Database")
  ssEfficiency = ss.getSheetByName("Efficiency-Calculator")
  ssFailedAttacks = ss.getSheetByName("Failed-Attacks")
  buttonLockMainDB = ss.getRangeByName("buttonLockMainDB")
  buttonAddRows = ss.getRangeByName("buttonAddRows")
  buttonExportEfficiency = ss.getRangeByName("buttonExportEfficiency")
  buttonFailedAttacks = ss.getRangeByName("buttonFailedAttacks")
  dateToday = Utilities.formatDate(new Date(), "GMT", "dd/MM/yyyy")
  dateParam = ss.getRangeByName("mainDBDate").getValue()

  //**********//
  //   main   //
  //**********//
  if (buttonLockMainDB.getValue() == true) {
    Logger.log("sheet is locked")
    return 0
  } else if (r.getRow() == buttonAddRows.getRow() && r.getColumn() == buttonAddRows.getColumn() && buttonAddRows.getValue() == true) {
    Logger.log("executing addData()")
    addData()
  } else if (r.getRow() == buttonExportEfficiency.getRow() && r.getColumn() == buttonExportEfficiency.getColumn() && buttonExportEfficiency.getValue() == true) {
    // export efficiency data to main database
    Logger.log("executing updateEfficiency()")
    updateEfficiency()
  } else if (r.getRow() == buttonFailedAttacks.getRow() && r.getColumn() == buttonFailedAttacks.getColumn() && buttonFailedAttacks.getValue() == true) {
    // export failed attacks data to failed-attacks database
    Logger.log("executing updateFailedAttacks()")
    updateFailedAttacks()
  }
}

function updateNamedRange(arrayRangeNameAndSheet) {
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
  updateNamedRange(["metrics", "Metrics"])
  updateNamedRange(["mainDB", "Database"])

  var members = ss.getRangeByName("members").getValues()
  var metrics = ss.getRangeByName("metrics").getValues()

  var output = []
  for (var x=0; x<members.length; x++) {
    for (var y=0; y<metrics.length; y++) {
      output.push([members[x], metrics[y], dateParam, null])
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
  updateNamedRange(["mainDB", "Database"])

  // sort database
  ss.getRangeByName("mainDB").sort([{column: 3, ascending: false}, {column: 1}])

  // find new last row and apply formula to generate primary key for lookup
  var newLastRow = ss.getRangeByName("mainDB").getLastRow()
  var lookupFormulaRange = ssDatabase.getRange("R2C5:R"+newLastRow+"C5")
  lookupFormulaRange.setFormula("=CONCATENATE(A2,B2,C2)")

  var dupeFormulaRange = ssDatabase.getRange("R2C6:R"+newLastRow+"C6")
  dupeFormulaRange.setFormula("=if(COUNTIF($E:$E,$E:$E)=1,FALSE(),TRUE())")

  // reset checkbox to false
  buttonAddRows.setValue("false")
  buttonLockMainDB.setValue("true")
}

function updateEfficiency() {
  updateNamedRange(["mainDB", "Database"])

  var efficiencyTable = ss.getRangeByName("efficiencyTable").getValues()
  Logger.log(efficiencyTable)

  var output = []
  efficiencyTable.forEach(
    function(row) {
      output.push([row[0], "Failed Attacks", dateParam, row[2]])
      output.push([row[0], "Efficiency", dateParam, row[4]])
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
  updateNamedRange(["mainDB", "Database"])

  // sort database
  ss.getRangeByName("mainDB").sort([{column: 3, ascending: false}, {column: 1}])

  // find new last row and apply formula to generate primary key for lookup
  var newLastRow = ss.getRangeByName("mainDB").getLastRow()
  var lookupFormulaRange = ssDatabase.getRange("R2C5:R"+newLastRow+"C5")
  lookupFormulaRange.setFormula("=CONCATENATE(A2,B2,C2)")

  var dupeFormulaRange = ssDatabase.getRange("R2C6:R"+newLastRow+"C6")
  dupeFormulaRange.setFormula("=if(COUNTIF($E:$E,$E:$E)=1,FALSE(),TRUE())")

  // reset checkbox to false
  buttonExportEfficiency.setValue("false")
  buttonLockMainDB.setValue("true")
}

// https://yagisanatode.com/2019/05/11/google-apps-script-get-the-last-row-of-a-data-range-when-other-columns-have-content-like-hidden-formulas-and-check-boxes/
function getLastRowSpecial(range){
  var rowNum = 0
  var blank = false
  for (var row = 0; row < range.length; row++) {
    if (range[row][0] === "" && !blank) {
      rowNum = row
      blank = true
    } else if (range[row][0] !== "") {
      blank = false
    }
  }
  return rowNum
}

function updateFailedAttacks() {
  updateNamedRange(["failedAttacksDB", "Failed-Attacks"])
  var columnToCheck = ssEfficiency.getRange("A:A").getValues()
  var currentFailedAttacksLastRow = getLastRowSpecial(columnToCheck)
  var currentFailedAttacks = ssEfficiency.getRange(2, 1, currentFailedAttacksLastRow -1, 4).getValues()  // -1 to exclude column header from the count
  Logger.log(currentFailedAttacks)

  var output = []
  currentFailedAttacks.forEach(
    function(row) {
      output.push([row[0], row[1], row[2], row[3], dateParam])
    }
  )
  Logger.log(output)

  var dbLastRow = ssFailedAttacks.getLastRow()
  var outputRange = ssFailedAttacks.getRange("R"+(dbLastRow+1)+"C1:R"+(dbLastRow+output.length)+"C5")
  outputRange.setValues(output)

  // update named range
  updateNamedRange(["failedAttacksDB", "Failed-Attacks"])

  // sort database
  ss.getRangeByName("failedAttacksDB").sort([{column: 5, ascending: false}, {column: 1}])

  // reset checkbox to false
  buttonFailedAttacks.setValue("false")
  buttonLockMainDB.setValue("true")
}
