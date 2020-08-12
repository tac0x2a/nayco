
const axios = require('axios').default

export default {
  listTables (callback) {
    axios.get('/api/v1/table/').then((res) => {
      callback(res.data)
    })
  }
}
