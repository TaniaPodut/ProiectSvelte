import type { ContactDetail, FeatureItem, ProductFormData } from '$lib/types';

export const navLinks = [
  { href: '/', label: 'Acasă', match: 'exact' },
  { href: '/products', label: 'Produse', match: 'startsWith' },
  { href: '/contact', label: 'Contact', match: 'exact' },
  { href: '/admin', label: 'Admin', match: 'startsWith', admin: true }
];

export const siteContent = {
  brandName: 'Magazin de Scaune Baia Mare',
  hero: {
    title: 'Proiectăm și construim scaune mai bune, pentru o viață mai bună',
    text: 'Într-un mic magazin din inima orașului Baia Mare, ne petrecem zilele perfecționând neîncetat scaunul. Rezultatul este un amestec perfect de frumusețe și confort, care va avea un impact de durată asupra sănătății dumneavoastră.',
    ctaLabel: 'Cumpără scaune',
    ctaHref: '/products',
    image: '/hero.jpg',
    imageAlt: 'Fotografie scaun'
  },
  featuresTitle: 'Ce face scaunele noastre speciale',
  testimonial: {
    image: '/customers.jpg',
    imageAlt: 'Oameni stând pe scaune',
    title: '"Nu am mai putea trăi fără aceste scaune"',
    quote: 'Scaunele de la Webtania ne-au schimbat complet modul în care lucrăm și ne relaxăm acasă. Calitatea este incredibilă și designul se potrivește perfect în livingul nostru.',
    author: 'Mary și Sarah Johnson'
  },
  featuredProductsTitle: 'Cele mai vândute scaune',
  allProductsCta: 'Vezi toate produsele →',
  productsTitle: 'Produsele noastre',
  contactTitle: 'Contactează-ne',
  contactIntro: 'Suntem aici să te ajutăm să găsești scaunul perfect. Vizitează-ne în showroom sau trimite-ne un mesaj.',
  contactInfoTitle: 'Informații de contact',
  showroomSchedule: ['Luni - Vineri: 09:00 - 18:00', 'Sâmbătă: 10:00 - 14:00'],
  footerPrefix: 'Drepturi de autor',
  footerText: 'de către Podut Tania. Toate drepturile rezervate.'
};

export const uiText = {
  common: {
    loading: 'Se încarcă...',
    empty: 'Nu există rezultate pentru selecția curentă.',
    priceCurrency: 'lei',
    featured: 'Featured',
    yes: 'Da',
    no: 'Nu',
    choose: 'Alege:',
    networkError: 'Eroare de rețea.'
  },
  products: {
    loading: 'Se încarcă produsele...',
    emptyForCategory: 'Niciun produs găsit în această categorie.',
    detailTitleFallback: 'Produs',
    detailPageTitle: 'Magazin de Scaune',
    detailLoadError: 'Eroare la încărcarea produsului.',
    backToProducts: 'Înapoi la produse',
    viewDetails: 'Vezi detalii',
    addToCart: 'Adaugă în coș →'
  },
  contact: {
    submitError: 'Eroare la trimiterea mesajului.',
    successMessage: 'Mesajul a fost trimis cu succes! Te vom contacta în cel mai scurt timp.',
    resetButton: 'Trimite alt mesaj',
    submitButton: 'Trimite mesajul',
    submitLoading: 'Se trimite...',
    scheduleTitle: 'Program Showroom:',
    fields: {
      name: { id: 'nume', label: 'Nume complet', placeholder: 'Ion Popescu' },
      phone: { id: 'telefon', label: 'Nr. de telefon', placeholder: '0744 123 456' },
      email: { id: 'email', label: 'Adresă de email', placeholder: 'ion.popescu@exemplu.ro' },
      message: { id: 'mesaj', label: 'Mesajul tău', placeholder: 'Cum te putem ajuta?' }
    }
  },
  admin: {
    title: 'Panou Admin',
    subtitle: 'Autentifică-te pentru a gestiona produsele',
    siteLink: 'Site principal',
    logout: 'Deconectare',
    loginButton: 'Autentifică-te',
    loginError: 'Credențiale incorecte.',
    addTitle: 'Adaugă produs nou',
    addButton: 'Adaugă produs',
    addProcessing: 'Se procesează...',
    addSuccess: 'Produs adăugat cu succes!',
    addError: 'Eroare la adăugare.',
    editTitle: 'Editează',
    editButton: 'Salvează',
    editProcessing: 'Se salvează...',
    editSuccess: 'Actualizat cu succes!',
    editError: 'Eroare la actualizare.',
    deleteConfirm: 'Ștergi {name}?',
    deleteError: 'Eroare la ștergere.',
    productsTitle: 'Produse existente',
    reload: 'Reîncarcă',
    productsEmpty: 'Nu există produse încă.',
    cancel: 'Anulează',
    tableHeaders: {
      id: 'ID',
      image: 'Imagine',
      name: 'Nume',
      category: 'Categorie',
      price: 'Preț',
      featured: 'Featured',
      actions: 'Acțiuni'
    },
    rowActions: {
      edit: 'Editează',
      delete: 'Șterge'
    },
    loginFields: {
      username: 'Utilizator',
      password: 'Parolă'
    },
    productForm: {
      name: 'Nume produs',
      category: 'Categorie',
      price: 'Preț (lei)',
      description: 'Descriere',
      image: 'Imagine',
      alt: 'Text alt',
      featured: 'Featured'
    }
  }
};

export const features: FeatureItem[] = [
  {
    title: 'Știința întâlnește designul',
    text: 'Folosim principii de ergonomie avansată pentru a crea scaune care susțin postura corectă a corpului tău pe tot parcursul zilei.',
    iconPath:
      'M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z'
  },
  {
    title: 'Confort maxim',
    text: 'Materialele premium și designul inovator garantează o experiență de relaxare de neegalat, indiferent de durata utilizării.',
    iconPath:
      'M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z'
  },
  {
    title: 'Etic și sustenabil',
    text: 'Suntem dedicați protejării mediului, folosind doar materiale ecologice și procese de producție responsabile în atelierul nostru.',
    iconPath:
      'M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z'
  }
];

export const contactDetails: ContactDetail[] = [
  {
    label: 'Strada Victoriei 12, Baia Mare, România',
    iconPath:
      'M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z M15 11a3 3 0 11-6 0 3 3 0 016 0z'
  },
  {
    label: '+40 744 123 456',
    iconPath:
      'M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z'
  },
  {
    label: 'contact@webtania.ro',
    iconPath:
      'M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z'
  }
];

export const emptyProduct: ProductFormData = {
  name: '',
  category: '',
  price: 0,
  description: '',
  image: '',
  alt: '',
  isFeatured: false
};
