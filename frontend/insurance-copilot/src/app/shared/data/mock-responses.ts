export interface MockResponse {
	content: string;
	type: 'text' | 'table';
	tableData?: any[];
}

export const directResponses: MockResponse[] = [
	{
		content: 'La cobertura de responsabilidad civil te protege ante daños a terceros en sus bienes o personas. Es fundamental para evitar gastos legales imprevistos.',
		type: 'text'
	},
	{
		content: 'Sí, la mayoría de pólizas Todo Riesgo incluyen asistencia mecánica y grúa las 24 horas. ¿Te gustaría saber el límite de kilómetros cubiertos por aseguradora?',
		type: 'text'
	},
	{
		content: 'El deducible es el monto que debes pagar en caso de siniestro antes de que la aseguradora cubra el resto. Un deducible más alto suele reducir el costo de la prima mensual.',
		type: 'text'
	}
];

export const comparisonResponses: MockResponse[] = [
	{
		content: 'Aquí tienes una comparativa de las coberturas principales entre Rimac y Pacífico para un uso particular:',
		type: 'table',
		tableData: [
			{ insurer: 'Rimac Seguros', premium: '$450/año', coverage: 'Robo Total, Choque, RC $100k' },
			{ insurer: 'Pacífico', premium: '$480/año', coverage: 'Robo Total, Choque, RC $150k + Chofer reemplazo' },
			{ insurer: 'La Positiva', premium: '$420/año', coverage: 'Robo Total, Choque, RC $80k' }
		]
	},
	{
		content: 'Analizando las exclusiones, estas son las diferencias clave que debes considerar:',
		type: 'table',
		tableData: [
			{ insurer: 'Rimac', premium: 'N/A', coverage: 'No cubre vías no autorizadas' },
			{ insurer: 'Pacífico', premium: 'N/A', coverage: 'No cubre conductores menores de 21 años sin recargo' },
			{ insurer: 'Mapfre', premium: 'N/A', coverage: 'Requiere GPS obligatorio para modelos de alto riesgo' }
		]
	}
];

export const quotationResponses: MockResponse[] = [
	{
		content: 'He generado las siguientes cotizaciones para tu Toyota Corolla 2024. Los precios incluyen IGV:',
		type: 'table',
		tableData: [
			{ insurer: 'Rimac - Basic', premium: '$38.50/mes', coverage: 'Pérdida Total' },
			{ insurer: 'Rimac - Plus', premium: '$55.00/mes', coverage: 'Todo Riesgo con Taller de Marca' },
			{ insurer: 'Pacífico - Full', premium: '$62.00/mes', coverage: 'Todo Riesgo Premium + Auto Reemplazo' }
		]
	}
];
