import type { AdminCredentials, ContactPayload, Order, OrderPayload, Product, ProductFormData } from '$lib/types';

async function parseJson<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let message = 'Cererea nu a reușit.';
    try {
      const error = await response.json();
      message = error.detail || error.message || message;
    } catch {
      // No JSON body
    }
    throw new Error(message);
  }
  return response.json() as Promise<T>;
}

function adminHeaders(token: string) {
  return {
    Authorization: `Bearer ${token}`
  };
}

export async function getProducts() {
  return parseJson<Product[]>(await fetch('/api/products'));
}

export async function getProduct(id: string | number) {
  return parseJson<Product>(await fetch(`/api/products/${id}`));
}

export async function sendContactMessage(payload: ContactPayload) {
  return parseJson<{ status: string }>(
    await fetch('/api/contact', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
  );
}

export async function createOrder(payload: OrderPayload) {
  return parseJson<Order>(
    await fetch('/api/orders', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
  );
}

export async function loginAdmin(credentials: { username: string; password: string }) {
  return parseJson<{ token: string }>(
    await fetch('/api/admin/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(credentials)
    })
  );
}

export async function logoutAdmin(token: string) {
  return parseJson<{ mesaj: string }>(
    await fetch('/api/admin/logout', {
      method: 'POST',
      headers: adminHeaders(token)
    })
  );
}

export async function getOrders(token: string) {
  return parseJson<Order[]>(
    await fetch('/api/orders', {
      headers: adminHeaders(token)
    })
  );
}

export async function getContactMessages(token: string) {
  return parseJson<ContactPayload[]>(
    await fetch('/api/contact', {
      headers: adminHeaders(token)
    })
  );
}

export async function createProduct(product: ProductFormData, token: string) {
  return parseJson<Product>(
    await fetch('/api/products', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...adminHeaders(token)
      },
      body: JSON.stringify(product)
    })
  );
}

export async function updateProduct(id: number, product: ProductFormData, token: string) {
  return parseJson<Product>(
    await fetch(`/api/products/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        ...adminHeaders(token)
      },
      body: JSON.stringify(product)
    })
  );
}

export async function deleteProduct(id: number, token: string) {
  const response = await fetch(`/api/products/${id}`, {
    method: 'DELETE',
    headers: adminHeaders(token)
  });
  if (!response.ok) {
    throw new Error('Produsul nu a putut fi șters.');
  }
}
