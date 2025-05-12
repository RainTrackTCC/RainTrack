const categorias = JSON.parse('{{ dados["categories"] | tojson | safe }}');
    const series = JSON.parse('{{ dados["series"] | tojson | safe }}');
        
    Highcharts.chart('container', {
        chart: { type: 'line' },
        title: { text: 'Teste' },
        xAxis: {
            categories: categorias,
            title: { text: 'Hora' }
        },
        yAxis: {
            title: { text: 'Valores' }
        },
        series: series
    });