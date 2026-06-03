export const allProductsFilter = {
  id: 'toate',
  label: 'Toate'
};

export const defaultProductCategories = ['Relaxare', 'Birou', 'Premium'];

export function buildCategoryFilters(categories: string[]) {
  const uniqueCategories = [...new Set(categories.filter(Boolean))];

  return [
    allProductsFilter,
    ...uniqueCategories.map((category) => ({
      id: category,
      label: category
    }))
  ];
}
