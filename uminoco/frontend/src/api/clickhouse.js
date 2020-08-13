
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
  }
}
