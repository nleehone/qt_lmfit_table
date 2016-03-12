import lmfit
from numpy import inf
from PySide.QtCore import QAbstractTableModel, QModelIndex, Qt


class QtLmfitTableModel(QAbstractTableModel):
    def __init__(self, parameters=None, parent=None):
        super().__init__(parent)

        if parameters is None:
            self.parameters = lmfit.Parameters()
        else:
            self.parameters = parameters

    def get_parameter(self, row):
        try:
            return self.parameters[list(self.parameters.keys())[row]]
        except IndexError:
            return None

    def rowCount(self, index=QModelIndex()):
        return len(self.parameters)

    def columnCount(self, index=QModelIndex()):
        return 6

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled

        # If the column is the vary parameter then we want the user to be able to check/uncheck the box
        if index.column() == 1:
            return Qt.ItemFlags(QAbstractTableModel.flags(self, index) | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable)

        return Qt.ItemFlags(QAbstractTableModel.flags(self, index) | Qt.ItemIsEditable)

    def setData(self, index, value, role=Qt.EditRole):
        if index.isValid() and 0 <= index.row() < len(self.parameters):
            parameter = self.get_parameter(index.row())
            if role == Qt.EditRole:
                try:
                    # We cannot set the name since this is tied to the parameters
                    if index.column() == 1:
                        parameter.set(vary=value, expr=parameter.expr)
                    elif index.column() == 2:
                        parameter.set(value=float(value), expr=parameter.expr)
                    elif index.column() == 3:
                        try:
                            parameter.set(min=float(value), expr=parameter.expr)
                        except ValueError as e:
                            print(e)
                            print('Value was not a valid float. Setting min to -Infinity.')
                            parameter.set(min=-inf, expr=parameter.expr)
                    elif index.column() == 4:
                        try:
                            parameter.set(max=float(value), expr=parameter.expr)
                        except ValueError as e:
                            print(e)
                            print('Value was not a valid float. Setting max to Infinity.')
                            parameter.set(max=inf, expr=parameter.expr)
                    elif index.column() == 5:
                        if value == '':
                            value = None
                        # TODO: Deal with recursive expressions
                        parameter.set(expr=value)
                    self.dataChanged.emit(index, index)
                except ValueError as e:
                    print(e)
                    return False
                return True
            elif role == Qt.CheckStateRole:
                try:
                    if index.column() == 1:
                        parameter.vary = value
                    self.dataChanged.emit(index, index)
                except ValueError as e:
                    print(e)
                    return False
                return True
        return False

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        if not 0 <= index.row() < len(self.parameters):
            return None

        parameter = self.get_parameter(index.row())

        if role == Qt.DisplayRole:
            if index.column() == 0:
                return parameter.name
            elif index.column() == 2:
                try:
                    return parameter.value
                except NameError as e:
                    # TODO: Check that this is the only way to get this error
                    # TODO: Check if there is a better place to check the expression that was entered
                    print('The expression you entered is not valid')
                    print(e)
            elif index.column() == 3:
                return parameter.min
            elif index.column() == 4:
                return parameter.max
            elif index.column() == 5:
                return parameter.expr
        elif role == Qt.CheckStateRole:
            if index.column() == 1:
                if parameter.expr is not None:
                    return Qt.PartiallyChecked
                return Qt.Checked if parameter.vary else Qt.Unchecked

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:
            return ["Name", "Vary", "Value", "Min", "Max", "Expr"][section]
