from PyQt5 import QtWidgets, QtCore, uic
import sys
from licorne import SampleModel,layer

Ui_layerselector, QtBaseClass = uic.loadUiType('UI/layerselector.ui')

class layerselector(QtWidgets.QWidget, Ui_layerselector):
    invalidSelection=QtCore.pyqtSignal(str)
    def __init__(self,sample_model,*args):
        QtWidgets.QWidget.__init__(self,*args)
        Ui_layerselector.__init__(self)
        self.setupUi(self)
        self.sample_model=sample_model
        self.sample_model.setParent(self)
        self.listView.setModel(self.sample_model)
        self.listView.selectionModel().selectionChanged.connect(self.selectionChanged)
        self.invalidSelection[str].connect(self.module_logger)

    def module_logger(self,message):
        print('[layerselector]: '+message)

    def addClicked(self):
        selected=self.listView.selectionModel().selectedRows()
        inds=sorted([s.row() for s in selected])
        if inds:
            for i in inds:
                if inds in [[0],[self.sample_model.rowCount()-1]]:
                    self.invalidSelection.emit('Cannot add another substrate or incoming media')
                else:
                    self.sample_model.addItem(self.sample_model.layers[i-1])
        else:
            self.sample_model.addItem(layer.Layer())
        self.listView.selectionModel().clear()
        for selection in selected:
            self.listView.selectionModel().select(selection,QtCore.QItemSelectionModel.Select)         

    def delClicked(self):
        inds=sorted([s.row() for s in self.listView.selectionModel().selectedRows()], reverse=True)
        if inds:
            if inds in [[0],[self.sample_model.rowCount()-1]]:
                self.invalidSelection.emit('Cannot delete substrate or incoming media')
            else:
                for i in inds:
                    self.sample_model.delItem(i-1)
        else:
            self.invalidSelection.emit("nothing selected")
            
    def selectionEntered(self):
        selection_string=str(self.select_lineEdit.text())
        slice_parts=selection_string.split(':')
        if len(slice_parts)>3:
            self.invalidSelection.emit(selection_string+" has more than three arguments")
            return
        if len(slice_parts)==1:
            try:
                index=int(slice_parts[0])
                selection_slice=slice(index,index+1)
            except ValueError:
                self.invalidSelection.emit(selection_string+' cannot be converted to a slice')
                return
        else:
            try:
                s=[int(x) if x.strip()!='' else None for x in slice_parts]
                selection_slice=slice(*s)
            except ValueError:
                self.invalidSelection.emit(selection_string+' cannot be converted to a slice')
                return
        self.listView.selectionModel().clear()
        all_layers=range(1,self.sample_model.rowCount()-1)
        new_selection=all_layers[selection_slice]
        for i in new_selection:
            layer_index=self.sample_model.index(i)
            self.listView.selectionModel().select(layer_index,QtCore.QItemSelectionModel.Select)

        
    def selectionChanged(self,selected,deselected):
        incoming_media_index=self.sample_model.index(0)
        substrate_index=self.sample_model.index(self.sample_model.rowCount()-1)
        all_rows=self.listView.selectionModel().selectedRows()
        if (substrate_index in all_rows) and len(all_rows)>1:
            if substrate_index in selected:
                if len(selected)>1:
                    self.listView.selectionModel().select(substrate_index,QtCore.QItemSelectionModel.Deselect)
                else:
                    self.listView.selectionModel().clear()
                    self.listView.selectionModel().select(substrate_index,QtCore.QItemSelectionModel.Select)             
            else:
                self.listView.selectionModel().select(substrate_index,QtCore.QItemSelectionModel.Deselect)
        if (incoming_media_index in all_rows) and len(all_rows)>1:
            if incoming_media_index in selected:
                if len(selected)>1:
                    self.listView.selectionModel().select(incoming_media_index,QtCore.QItemSelectionModel.Deselect)
                else:
                    self.listView.selectionModel().clear()
                    self.listView.selectionModel().select(incoming_media_index,QtCore.QItemSelectionModel.Select)             
            else:
                self.listView.selectionModel().select(incoming_media_index,QtCore.QItemSelectionModel.Deselect)


if __name__=='__main__':
    app = QtWidgets.QApplication(sys.argv)
    sm=SampleModel.SampleModel()
    sm.addItem(layer.Layer(name='L0'))
    sm.addItem(layer.Layer(name='L1',thickness=2))
    sm.addItem(layer.Layer(name='L2'))
    sm.addItem(layer.Layer(name='L3'))
    window = layerselector(sm)
    window.show()
    sys.exit(app.exec_())

