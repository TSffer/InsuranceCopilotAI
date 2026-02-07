import {
	User,
	Message,
	ChatSession,
	InsuranceQuote,
	ComparisonResult,
	ComparisonTableRow,
	SourceDocument,
	QueryAnalysis,
} from '../models/types';

// ============ USUARIOS MOCK ============

export const mockUsers = {
	broker1: {
		id: 'user-001',
		email: 'broker@seguros.com',
		firstName: 'Carlos',
		lastName: 'Mendoza',
		createdAt: new Date('2024-01-15'),
		role: 'broker' as const,
	} as User,
	broker2: {
		id: 'user-002',
		email: 'juan.perez@seguros.com',
		firstName: 'Juan',
		lastName: 'Pérez',
		createdAt: new Date('2024-02-20'),
		role: 'broker' as const,
	} as User,
};

// ============ MENSAJES MOCK ============

export const mockMessages = {
	user1: {
		id: 'msg-001',
		content: 'Cotiza una Toyota Hilux 2023 en Rimac y Pacífico',
		role: 'user' as const,
		timestamp: new Date('2024-02-01T10:00:00'),
		status: 'sent' as const,
	} as Message,
	assistant1: {
		id: 'msg-002',
		content:
			'He encontrado 2 cotizaciones para tu Toyota Hilux 2023. Rimac ofrece una prima de S/ 2,500 al año con cobertura integral. Pacífico ofrece S/ 2,350 con opciones flexibles. ¿Deseas ver la comparación detallada de cláusulas?',
		role: 'assistant' as const,
		timestamp: new Date('2024-02-01T10:05:00'),
		status: 'sent' as const,
		metadata: {
			type: 'quote' as const,
		},
	} as Message,
};

// ============ COTIZACIONES MOCK ============

export const mockQuotes: InsuranceQuote[] = [
	{
		id: 'quote-rimac-001',
		insurer: 'Rimac Seguros',
		premium: 2500,
		currency: 'PEN',
		coverage: {
			type: 'Integral',
			limit: 'Sin límite',
			description: 'Cobertura completa incluyendo robo, colisión y responsabilidad civil',
		},
		clausesHighlight:
			'Cubre daños por accidentes, robo, vandalismo. Deducible: 5% con mínimo S/ 500',
		metadata: {
			responseTime: 250,
			dataSource: 'database' as const,
		},
		link: '#',
	},
	{
		id: 'quote-pacifico-001',
		insurer: 'Pacífico Seguros',
		premium: 2350,
		currency: 'PEN',
		coverage: {
			type: 'Flexible',
			limit: 'Customizable',
			description: 'Opciones flexibles adaptables a tu presupuesto',
		},
		clausesHighlight: 'Cobertura de daños, robo y terceros. Deducible desde S/ 250',
		metadata: {
			responseTime: 180,
			dataSource: 'database' as const,
		},
		link: '#',
	},
	{
		id: 'quote-positiva-001',
		insurer: 'Positiva Seguros',
		premium: 2200,
		currency: 'PEN',
		coverage: {
			type: 'Estándar',
			limit: 'Hasta S/ 50,000',
			description: 'Cobertura estándar con asistencia 24/7',
		},
		clausesHighlight: 'Cobertura básica con asistencia. Deducible: 8% con mínimo S/ 400',
		metadata: {
			responseTime: 320,
			dataSource: 'database' as const,
		},
		link: '#',
	},
];

// ============ TABLA COMPARATIVA MOCK ============

export const mockComparisonTable: ComparisonTableRow[] = [
	{
		insurer: 'Rimac Seguros',
		premium: 'S/ 2,500/año',
		coverage: 'Integral sin límite',
		specialClause: 'Uso en vías no autorizadas: Cubierto con 15% recargo',
		advantages: [
			'Red de talleres más amplia',
			'Asesor personal asignado',
			'Cobertura integral',
		],
		disadvantages: ['Prima más alta', 'Deducible mínimo de S/ 500'],
		responsiveness: 'Respuesta inmediata',
	},
	{
		insurer: 'Pacífico Seguros',
		premium: 'S/ 2,350/año',
		coverage: 'Flexible y customizable',
		specialClause: 'Uso en vías no autorizadas: Cobertura opcional - Adicional S/ 150',
		advantages: ['Mejor relación precio-cobertura', 'Deducible bajo desde S/ 250'],
		disadvantages: ['Menos talleres convenios', 'Cobertura más limitada que Rimac'],
		responsiveness: 'Respuesta dentro de 2 horas',
	},
	{
		insurer: 'Positiva Seguros',
		premium: 'S/ 2,200/año',
		coverage: 'Estándar hasta S/ 50,000',
		specialClause: 'Uso en vías no autorizadas: No cubierto',
		advantages: ['Prima más económica', 'Asistencia 24/7'],
		disadvantages: ['Cobertura limitada', 'No incluye vías no autorizadas'],
		responsiveness: 'Respuesta en 24 horas',
	},
];

// ============ DOCUMENTOS FUENTE MOCK ============

export const mockSourceDocuments: SourceDocument[] = [
	{
		id: 'doc-rimac-001',
		insurer: 'Rimac Seguros',
		documentType: 'policy',
		title: 'Póliza Integral Automóvil 2024',
		relevantClause:
			'Art. 12: El uso en vías no autorizadas está cubierto bajo las siguientes condiciones: El vehículo debe estar matriculado y el conductor debe poseer licencia de conducir válida.',
		pageReference: 'Página 45',
		similarity: 0.98,
		extractedAt: new Date('2024-01-30'),
	},
	{
		id: 'doc-pacifico-001',
		insurer: 'Pacífico Seguros',
		documentType: 'coverage_map',
		title: 'Mapa de Coberturas Flexible',
		relevantClause:
			'Cláusula Adicional: El uso en vías no autorizadas puede incluirse pagando un recargo del 3% sobre la prima base. Limitado a 30 días al año.',
		pageReference: 'Anexo B, Página 12',
		similarity: 0.92,
		extractedAt: new Date('2024-01-29'),
	},
	{
		id: 'doc-positiva-001',
		insurer: 'Positiva Seguros',
		documentType: 'conditions',
		title: 'Condiciones Generales',
		relevantClause:
			'Exclusión: El seguro NO cubre daños causados en vías no autorizadas, caminos privados sin mantenimiento o terrenos sin carreteras definidas.',
		pageReference: 'Sección Exclusiones, Página 8',
		similarity: 0.89,
		extractedAt: new Date('2024-01-28'),
	},
];

// ============ ANÁLISIS DE QUERY MOCK ============

export const mockQueryAnalysis: QueryAnalysis = {
	intent: 'comparison',
	confidence: 0.95,
	extractedParameters: {
		vehicle: {
			brand: 'Toyota',
			model: 'Hilux',
			year: 2023,
			type: 'Pickup',
		},
		insurers: ['Rimac', 'Pacífico'],
		clauses: ['Uso en vías no autorizadas'],
	},
};

// ============ RESULTADO COMPARATIVO MOCK ============

export const mockComparisonResult: ComparisonResult = {
	id: 'comparison-001',
	query: 'Cotiza una Toyota Hilux 2023 en Rimac y Pacífico, y compárame la cláusula de "Uso en vías no autorizadas"',
	quotes: mockQuotes,
	comparativeTable: mockComparisonTable,
	analysis:
		'Rimac ofrece la cobertura más completa para uso en vías no autorizadas, incluyéndola en su póliza integral. Pacífico ofrece una opción flexible a menor costo pero con restricciones. Positiva no cubre este riesgo. Para un broker que maneja clientes que requieren máxima flexibilidad, Rimac es la mejor opción.',
	timestamp: new Date(),
	sourceDocuments: mockSourceDocuments,
	metadata: {
		processingTime: 1250,
		vectorSimilarity: 0.94,
		dataQuality: 0.96,
	},
};

// ============ SESIÓN CHAT MOCK ============

export const mockChatSession: ChatSession = {
	id: 'session-001',
	userId: 'user-001',
	title: 'Análisis Toyota Hilux - Feb 2024',
	createdAt: new Date('2024-02-01T09:00:00'),
	updatedAt: new Date('2024-02-01T10:30:00'),
	messages: [
		mockMessages.user1,
		mockMessages.assistant1,
		{
			id: 'msg-003',
			content: 'Sí, por favor muestra la comparación detallada',
			role: 'user',
			timestamp: new Date('2024-02-01T10:06:00'),
			status: 'sent',
		} as Message,
		{
			id: 'msg-004',
			content: 'Aquí te muestro la tabla comparativa...',
			role: 'assistant',
			timestamp: new Date('2024-02-01T10:07:00'),
			status: 'sent',
			metadata: {
				type: 'table',
				data: mockComparisonTable,
			},
		} as Message,
	],
};

// ============ SESIONES MOCK ============

export const mockSessions: ChatSession[] = [mockChatSession];

// ============ FUNCIÓN AUXILIAR PARA OBTENER MOCK ============

export function getMockResponse<T>(
	type: 'quotes' | 'comparison' | 'analysis' | 'messages',
	delayMs: number = 800
): Promise<T> {
	return new Promise((resolve) => {
		setTimeout(() => {
			const responses: Record<string, unknown> = {
				quotes: mockQuotes,
				comparison: mockComparisonResult,
				analysis: mockQueryAnalysis,
				messages: mockMessages,
			};
			resolve(responses[type] as T);
		}, delayMs);
	});
}

// ============ OBJETO CENTRALIZADO CON TODOS LOS DATOS MOCK ============

export const mockData = {
	users: Object.values(mockUsers),
	messages: mockMessages,
	quotes: mockQuotes,
	comparisonResult: mockComparisonResult,
	comparisonTable: mockComparisonTable,
	sourceDocuments: mockSourceDocuments,
	queryAnalysis: mockQueryAnalysis,
	chatSession: mockChatSession,
	sessions: mockSessions,
};
