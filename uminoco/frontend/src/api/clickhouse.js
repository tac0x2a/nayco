
const axios = require('axios').default

export default {
  listTables (callback) {
    axios.get('/api/v1/table/').then((res) => {
      callback(res.data)
    })
  },

  tableDetail (tableName, callback, errorCallback) {
    axios.get('/api/v1/table/' + tableName).then((res) => {
      callback(res.data)
    }).catch((err) => {
      errorCallback(err)
    })
  },

  calHeatmapMax (tableName, callback, errorCallback) {
    axios.get('/api/v1/table/' + tableName + '/cal-heatmap-max').then((res) => {
      callback(res.data)
    }).catch((err) => {
      errorCallback(err)
    })
  },

  renameTable (currentTableName, newTableName, callback, errorCallback) {
    const param = new FormData()
    param.set('new_table_name', newTableName)

    axios.post('/api/v1/table/' + currentTableName + '/' + 'rename', param).then((res) => {
      callback(res.data)
    }).catch((err) => {
      errorCallback(err)
    })
  },

  dropTable (tableName, callback, errorCallback) {
    axios.post('/api/v1/table/' + tableName + '/' + 'drop').then((res) => {
      callback(res.data)
    }).catch((err) => {
      errorCallback(err)
    })
  },

  migrateTable (srcTableName, dstTableName, srcColumns, dstColumns, callback, errorCallback) {
    const param = new FormData()
    param.set('src_table_name', srcTableName)
    param.set('dst_table_name', dstTableName)
    param.set('src_columns', JSON.stringify(srcColumns))
    param.set('dst_columns', JSON.stringify(dstColumns))

    axios.post('/api/v1/migrate_table', param).then((res) => {
      callback(res.data)
    }).catch((err) => {
      errorCallback(err)
    })
  },

  listSources(callback, errorCallback) {
    axios.get('/api/v1/source/').then((res) => {
      callback(res.data)
    }).catch((err) => {
      errorCallback(err)
    })
  },

  sourceSpecifiedTypes(sourceId, callback, errorCallback) {
    axios.get('/api/v1/source_types/' + sourceId).then((res) => {
      callback(res.data)
    }).catch((err) => {
      errorCallback(err)
    })
  },

  updateSourceTypes(sourceId, sourceTypes, callback, errorCallback) {
    const param = new FormData()
    param.set('new_specified_types', JSON.stringify(sourceTypes))
    axios.post('/api/v1/source_types/' + sourceId + '/' + 'apply', param).then((res) => {
      callback(res.data)
    }).catch((err) => {
      errorCallback(err)
    })
  }
}
