package ui.viewResultTableModels;

import java.io.File;
import java.util.ArrayList;

import javax.swing.event.*;
import javax.swing.table.AbstractTableModel;

import modules.PluginModule;
import org.jetbrains.annotations.Nls;

import models.bean.*;
import services.RankingService;

public class MethodTableModel extends AbstractTableModel {
    private static final String[] columnNames = {"File name", "Method name", "Score", "Modified Score", "Line"};

    public static final int FILE_NAME_COLUMN_INDEX = 0;
    public static final int NAME_COLUMN_INDEX = 1;
    public static final int SCORE_COLUMN_INDEX = 2;
    public static final int MODIFIED_SCORE_COLUMN_INDEX = 3;
    public static final int LINE_COLUMN_INDEX = 4;

    private final ArrayList<TableData> tableDataList = new ArrayList<>();

    private final String spectraMetrics;
    private final String selectedRankType;


    public MethodTableModel(TestData testData, String spectraMetrics, String selectedRankType) {
        parseData(testData);
        setRanks();
        this.spectraMetrics = spectraMetrics;
        this.selectedRankType = selectedRankType;

    }

    private void parseData(TestData data) {
        for (ClassTestData classData : data.getClasses()) {
            String relativePath = classData.getRelativePath();

            for (ITestData methodData : classData.getElements()) {
                TableData methodTableData = new TableData();
                methodTableData.setName(methodData.getSuperName() + File.separator + methodData.getName());
                methodTableData.setPath(relativePath);
                methodTableData.setLine(methodData.getLine());
                methodTableData.setBarinelScore(methodData.getBarinel());
                methodTableData.setBarinelModifiedScore(methodData.getBarinelModified());
                methodTableData.setTarantulaScore(methodData.getTarantula());
                methodTableData.setOchiaiScore(methodData.getOchiai());
                methodTableData.setWong2Score(methodData.getWong2());
                methodTableData.setFaulty(methodData.isFaulty());
                methodTableData.setLevel(TableData.METHOD_LEVEL);
                if (methodData.getName().equalsIgnoreCase("<not_method>"))
                    continue;
                this.tableDataList.add(methodTableData);
            }
        }
    }

    private void setRanks(){
        ArrayList<Double> scoreList = new ArrayList<>();
        for(var tableData : this.tableDataList){
            if (PluginModule.isTarantulaSelected()) {
                scoreList.add(tableData.getTarantulaScore());
            } else if (PluginModule.isOchiaiSelected()) {
                scoreList.add(tableData.getOchiaiScore());
            } else if (PluginModule.isWongIISelected() || PluginModule.isDStarSelected()) {
                scoreList.add(tableData.getWong2Score());
            } else if (PluginModule.isBarinelSelected()){
                scoreList.add(tableData.getBarinelScore());
            }
        }

        RankingService rankingService = new RankingService(scoreList);
        ArrayList<Double> minRankList = rankingService.minRanking();
        ArrayList<Double> maxRankList = rankingService.maxRanking();
        ArrayList<Double> avgRankList = rankingService.averageRanking();
        for (int i=0; i<this.tableDataList.size(); i++){
            this.tableDataList.get(i).setAvgRank(avgRankList.get(i));
            this.tableDataList.get(i).setMinRank(minRankList.get(i));
            this.tableDataList.get(i).setMaxRank(maxRankList.get(i));
        }
    }

    @Override
    public int getRowCount() {
        return tableDataList.size();
    }

    @Override
    public int getColumnCount() {
        return columnNames.length;
    }

    @Nls
    @Override
    public String getColumnName(int columnIndex) {
        return columnNames[columnIndex];
    }

    @Override
    public Class<?> getColumnClass(int columnIndex) {
        switch (columnIndex) {
            case FILE_NAME_COLUMN_INDEX:
            case NAME_COLUMN_INDEX:
                return String.class;
            case SCORE_COLUMN_INDEX:
            case MODIFIED_SCORE_COLUMN_INDEX:
            case LINE_COLUMN_INDEX:
                return Double.class;
            default:
                return Object.class;
        }
    }

    @Override
    public boolean isCellEditable(int rowIndex, int columnIndex) {
        return false;
    }

    @Override
    public Object getValueAt(int rowIndex, int columnIndex) {
        TableData tableDataAtRowIndex = tableDataList.get(rowIndex);
        switch (columnIndex) {
            case FILE_NAME_COLUMN_INDEX:
                    return tableDataAtRowIndex.getPath();


            case NAME_COLUMN_INDEX:

                    return tableDataAtRowIndex.getName();

            case SCORE_COLUMN_INDEX:
                if (spectraMetrics.equals(" (Tarantula)")) {
                    return tableDataAtRowIndex.getTarantulaScore();
                } else if (spectraMetrics.equals(" (Ochiai)")) {
                    return tableDataAtRowIndex.getOchiaiScore();
                } else if (spectraMetrics.equals(" (WongII)") || spectraMetrics.equals(" (DStar)")) {
                    return tableDataAtRowIndex.getWong2Score();
                } else if (spectraMetrics.equals(" (Barinel)")){
                    return tableDataAtRowIndex.getBarinelScore();
                }
                else {
                    return -1;
                }
            case MODIFIED_SCORE_COLUMN_INDEX:
                if (spectraMetrics.equals(" (Barinel)")){
                    return tableDataAtRowIndex.getBarinelModifiedScore();
                }
                else {
                    return -1;
                }
            case LINE_COLUMN_INDEX:
                /*if(selectedRankType.equals(Resources.get("titles", "average_button"))){
                    return tableDataAtRowIndex.getAvgRank();
                }else if (selectedRankType.equals(Resources.get("titles", "minimum_button"))){
                    return tableDataAtRowIndex.getMinRank();
                }else if(selectedRankType.equals(Resources.get("titles", "maximum_button"))){
                    return tableDataAtRowIndex.getMaxRank();
                }else {
                    return -1;
                }*/
                return tableDataAtRowIndex.getLine();
            default:
                return "";
        }
    }

    @Override
    public void setValueAt(Object aValue, int rowIndex, int columnIndex) {

    }

    @Override
    public void addTableModelListener(TableModelListener listener) {

    }

    @Override
    public void removeTableModelListener(TableModelListener listener) {

    }
}