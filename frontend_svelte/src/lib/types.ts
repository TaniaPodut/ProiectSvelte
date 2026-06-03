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
};

export type AdminCredentials = {
  username: string;
  password: string;
};
