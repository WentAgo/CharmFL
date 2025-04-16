package ui.viewResultTableModels;

import models.bean.*;

import javax.swing.table.AbstractTableModel;
import java.util.ArrayList;
import java.util.Map;

public class TestTableModel  extends AbstractTableModel {

    private final ArrayList<TableData> tableDataList = new ArrayList<>();

    public TestTableModel(ViewTestData testData) {
        parseData(testData);
    }
    private void parseData(ViewTestData testData) {
        for (Map.Entry<String, ArrayList> entry : testData.getTests().entrySet()) {
            String testname = entry.getKey();
            ArrayList<String> values = entry.getValue();

            if (values.size() < 2) {
                continue;
            }

            String result = values.get(0);
            String heuristic = values.get(1);

            TableData tableData = new TableData();
            tableData.setTestName(testname);
            tableData.setTestResult(result);
            tableData.setTestHeuristic(heuristic);

            this.tableDataList.add(tableData);
        }
    }

    @Override
    public int getRowCount() {
        return 0;
    }

    @Override
    public int getColumnCount() {
        return 0;
    }

    @Override
    public Object getValueAt(int rowIndex, int columnIndex) {
        return null;
    }
}
