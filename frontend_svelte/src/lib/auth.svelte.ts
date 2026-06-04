import { browser } from '$app/environment';
import { loginAdmin, logoutAdmin } from '$lib/api';
import type { UserRole } from '$lib/types';

const TOKEN_KEY = 'webtania_admin_token';
const ROLE_KEY = 'webtania_user_role';
const DISPLAY_NAME_KEY = 'webtania_display_name';

class AuthState {
	token = $state<string | null>(null);
	role = $state<UserRole | null>(null);
	displayName = $state<string | null>(null);
	isHydrated = $state(false);

	hydrate() {
		if (!browser || this.isHydrated) return;
		this.token = localStorage.getItem(TOKEN_KEY);
		this.role = localStorage.getItem(ROLE_KEY) as UserRole | null;
		this.displayName = localStorage.getItem(DISPLAY_NAME_KEY);
		this.isHydrated = true;
	}

	async login(credentials: { username: string; password: string }) {
		const { token, role, display_name } = await loginAdmin(credentials);
		this.token = token;
		this.role = role;
		this.displayName = display_name;
		if (browser) {
			localStorage.setItem(TOKEN_KEY, token);
			localStorage.setItem(ROLE_KEY, role);
			localStorage.setItem(DISPLAY_NAME_KEY, display_name);
		}
	}

	get dashboardHref() {
		if (this.role === 'admin') return '/admin';
		if (this.role === 'manager') return '/manager';
		if (this.role === 'client') return '/client';
		return this.token ? '/admin' : '/login';
	}

	async logout() {
		if (this.token) {
			try {
				await logoutAdmin(this.token);
			} catch {
				// Ignore
			}
		}
		this.token = null;
		this.role = null;
		this.displayName = null;
		if (browser) {
			localStorage.removeItem(TOKEN_KEY);
			localStorage.removeItem(ROLE_KEY);
			localStorage.removeItem(DISPLAY_NAME_KEY);
		}
	}
}

export const authState = new AuthState();
