export type Product = {
  id: number;
  name: string;
  category: string;
  price: number;
  description: string;
  image: string;
  alt: string;
  isFeatured: boolean;
};

export type ProductFormData = Omit<Product, 'id'>;

export type FeatureItem = {
  title: string;
  text: string;
  iconPath: string;
};

export type ContactDetail = {
  label: string;
  iconPath: string;
};

export type ContactPayload = {
  nume: string;
  telefon: string;
  email: string;
  mesaj: string;
};

export type OrderPayload = {
  contact_name: string;
  contact_email: string;
  contact_phone: string;
  delivery_address: string;
  produs_id: number;
  quantity: number;
  special_requests?: string | null;
};

export type Order = OrderPayload & {
  id: number;
  status: string;
  created_at: string;
};

export type AdminCredentials = {
  username: string;
  password: string;
};

export type UserRole = 'admin' | 'manager';

export type User = {
	id: number;
	email: string;
	display_name: string;
	role: UserRole;
	is_active: boolean;
	created_at: string;
};

export type LoginRequestPayload = {
	email: string;
	password: string;
};

export type SessionResponse = {
	session_token: string;
	user: User;
};

export type StaffUserCreatePayload = {
	email: string;
	display_name: string;
	password: string;
	role: UserRole;
};

export type StaffUserUpdatePayload = {
	display_name?: string;
	role?: UserRole;
	is_active?: boolean;
};
