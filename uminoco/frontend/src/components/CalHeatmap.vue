<template>
  <div>

      <div v-show="max">
        <div id="cal-heatmap"></div>
        <!-- TODO: Fix cal-heatmap navigation bugs -->
        <!-- <v-btn id="prev" x-small color="primary">&lt;</v-btn>
        <v-btn v-on:click="reset" id="reset" x-small color="primary">now</v-btn>
        <v-btn id="next" x-small color="primary">&gt;</v-btn> -->
      </div>
      <div v-show="!max">
        loading... {{this.failer}}
      </div>

  </div>
</template>

<script>
import Clickhouse from '@/api/clickhouse.js'
// import CalHeatMap from 'cal-heatmap'
import CalHeatMap from '@/assets/scripts/cal-heatmap.js'

var cal = null

export default {
  props: {
    tableName: String
  },
  data: () => ({
    max: 0,
    failer: null
  }),
  mounted() {
  },

  watch: {
    tableName: {
      handler() {
        Clickhouse.calHeatmapMax(this.tableName, res => {
          this.max = res.max
        },
        err => {
          this.failer = { error: err, message: err?.response?.data?.message }
        })
      },
      immediate: true
    },
    max: {
      handler() {
        cal = new CalHeatMap()

        const startAt = new Date()
        startAt.setMonth(startAt.getMonth() - 3)
        cal.init({
          cellSize: 12,
          domain: 'month',
          subdomain: 'day',
          domainLabelFormat: '%b',
          subDomainDateFormat: '%Y-%m-%d',
          subDomainTextFormat: '%d',
          start: startAt,
          range: 4,
          label: {
            position: 'bottom'
          },
          tooltip: true,
          animationDuration: 100,
          data: '/api/v1/table/' + this.tableName + '/cal-heatmap?start={{t:start}}&end={{t:end}}',
          displayLegend: false,
          itemName: ['data<br>', 'data<br>'],
          previousSelector: '#prev',
          nextSelector: '#next',
          legend: [0, this.max * 0.25, this.max * 0.50, this.max * 0.75, this.max],
          legendColors: ['#FFFF99', '#FF9922']
        })
      }
    }
  },

  methods: {
    reset() {
      if (cal) {
        cal.rewind()
      }
    }
  }
}
</script>

<style>
  @import '../assets/styles/cal-heatmap.css'
</style>
