import { apiBasePath, sessionHeaderName } from '$lib/config';
import type {
	Product,
	ProductFormData,
	Order,
	OrderPayload,
	ContactPayload,
	AdminCredentials,
    User,
    SessionResponse,
    LoginRequestPayload,
    StaffUserCreatePayload,
    StaffUserUpdatePayload
} from '$lib/types';

type ApiRequestOptions = RequestInit & {
	sessionToken?: string;
};

export class ApiError extends Error {
	status: number;
	detail?: any;

	constructor(status: number, detail?: any) {
		super(typeof detail === 'string' ? detail : 'API request failed.');
		this.name = 'ApiError';
		this.status = status;
		this.detail = detail;
	}
}

async function readResponseData(response: Response): Promise<unknown> {
	const contentType = response.headers.get('content-type') ?? '';
	if (!contentType.includes('application/json')) {
		return null;
	}
	return await response.json();
}

function buildHeaders(headersInit: HeadersInit | undefined, sessionToken?: string): Headers {
	const headers = new Headers(headersInit);
	if (sessionToken) {
		headers.set(sessionHeaderName, sessionToken);
	}
	return headers;
}

export async function apiRequest<T>(path: string, options: ApiRequestOptions = {}): Promise<T> {
	const { sessionToken, headers: headersInit, ...requestInit } = options;
	const response = await fetch(`${apiBasePath}${path}`, {
		...requestInit,
		headers: buildHeaders(headersInit, sessionToken)
	});
	const data = await readResponseData(response);

	if (!response.ok) {
		const detail = (data as any)?.detail || 'A apărut o eroare.';
		throw new ApiError(response.status, detail);
	}

	return data as T;
}

export function getApiErrorMessage(error: unknown, fallbackMessage: string): string {
	if (error instanceof ApiError) {
		if (typeof error.detail === 'string') return error.detail;
		if (Array.isArray(error.detail)) return error.detail.map((d: any) => d.msg).join(' ');
	}
	return fallbackMessage;
}

// --- Public API ---

export function getProducts() {
	return apiRequest<Product[]>('/products');
}

export function getProduct(id: string | number) {
	return apiRequest<Product>(`/products/${id}`);
}

export function sendContactMessage(payload: ContactPayload) {
	return apiRequest<{ status: string }>('/contact', {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify(payload)
	});
}

export function createOrder(payload: OrderPayload) {
	return apiRequest<Order>('/orders', {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify(payload)
	});
}

// --- Auth API ---

export function loginStaff(payload: LoginRequestPayload): Promise<SessionResponse> {
	return apiRequest<SessionResponse>('/auth/login', {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify(payload)
	});
}

export async function logoutStaff(sessionToken: string): Promise<void> {
	await apiRequest('/auth/logout', {
		method: 'POST',
		sessionToken
	});
}

export function fetchCurrentUser(sessionToken: string): Promise<User> {
	return apiRequest<User>('/auth/me', { sessionToken });
}

// --- Protected API ---

export function getOrders(sessionToken: string) {
	return apiRequest<Order[]>('/orders', { sessionToken });
}

export function uploadImage(file: File, sessionToken: string) {
	const formData = new FormData();
	formData.append('fisier', file);
	return apiRequest<{ filename: string }>('/upload', {
		method: 'POST',
		sessionToken,
		body: formData
	});
}

export function createProduct(product: ProductFormData, sessionToken: string) {
	return apiRequest<Product>('/products', {
		method: 'POST',
		sessionToken,
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify(product)
	});
}

export function updateProduct(id: number, product: ProductFormData, sessionToken: string) {
	return apiRequest<Product>(`/products/${id}`, {
		method: 'PUT',
		sessionToken,
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify(product)
	});
}

export function deleteProduct(id: number, sessionToken: string) {
	return apiRequest(`/products/${id}`, {
		method: 'DELETE',
		sessionToken
	});
}

export function fetchStaffUsers(sessionToken: string): Promise<User[]> {
	return apiRequest<User[]>('/users', { sessionToken });
}

export function createStaffUser(sessionToken: string, payload: StaffUserCreatePayload): Promise<User> {
	return apiRequest<User>('/users', {
		method: 'POST',
		sessionToken,
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify(payload)
	});
}
