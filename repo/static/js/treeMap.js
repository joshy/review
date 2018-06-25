$(function () {
    if ('treeMap' === $('body').data('page')) {
    }

});

function treeMapModuleLoaded() {
    com.macrofocus.treemap.TreeMap.setLicenseKey("My Company", "ABC12-ABC12-ABC12-ABC12-ABC12-ABC12");
    treeMap = new com.macrofocus.treemap.TreeMap("treeMap");
    treeMap.loadJavaScriptArray(rows)
}

function treeMapModelLoaded() {
    //treeMap.setToolTipByNames("schreiber", "freigeber", "jaccars_s_f", "jaccard_g_f");
    var treeMapModel = treeMap.getModel();
    var treeMapSettings = treeMapModel.getSettings();
    var fieldSettings = treeMapSettings.getDefaultFieldSettings();
    fieldSettings.setAlgorithm(com.macrofocus.treemap.AlgorithmFactory.SQUARIFIED);
}
