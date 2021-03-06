from __future__ import (absolute_import, division, print_function)
from PyQt5 import QtCore
import os, copy
import licorne.experimental_data


class data_model(QtCore.QAbstractListModel):
    def __init__(self, *args, **kwargs):
        '''
        Create a data model
        '''
        QtCore.QAbstractListModel.__init__(self, *args, **kwargs)
        self.datasets = []
        self.background = 0.0
        self.theory_factor = 1.0
        self.experiment_factor = 1.0

    def __deepcopy__(self, memodict={}):
        cls = self.__class__
        result = cls.__new__(cls)
        result.datasets = copy.deepcopy(self.datasets)
        result.background = self.background
        result.theory_factor = self.theory_factor
        result.experiment_factor = self.experiment_factor
        return result

    def set_model(self, other):
        self.beginResetModel()
        self.datasets = copy.deepcopy(other.datasets)
        self.background = other.background
        self.theory_factor = other.theory_factor
        self.experiment_factor = other.experiment_factor
        self.endResetModel()

    def rowCount(self, parent=None):
        '''
        UI related
        returns numbers of data sets
        '''
        return len(self.datasets)

    def data(self, index, role):
        '''
        UI related
        function to return the filenames
        '''
        display_names = [os.path.basename(d.filename) for d in self.datasets]
        if not index.isValid():
            return QtCore.QVariant()
        elif role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()
        return QtCore.QVariant(display_names[index.row()])

    def addItem(self, item):
        '''
        UI and data related
        add a single dataset at the end of the list
        '''
        position = len(self.datasets)
        if not isinstance(item, licorne.experimental_data.experimental_data):
            return
        self.beginInsertRows(QtCore.QModelIndex(), position, position)
        self.datasets.insert(position, item)
        self.endInsertRows()

    def delItem(self, position):
        '''
        UI and data related
        delete a single dataset.
        The position is the index in the self.datasets
        This allows to handle UI stuff
        '''
        if position in range(len(self.datasets)):
            self.beginRemoveRows(QtCore.QModelIndex(), position, position)
            del self.datasets[position]
            self.endRemoveRows()
