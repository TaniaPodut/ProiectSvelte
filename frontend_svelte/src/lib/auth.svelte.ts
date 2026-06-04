import { browser } from '$app/environment';
import { loginAdmin, logoutAdmin } from '$lib/api';

const TOKEN_KEY = 'webtania_admin_token';

class AuthState {
	token = $state<string | null>(null);
	isHydrated = $state(false);

	hydrate() {
		if (!browser || this.isHydrated) return;
		this.token = localStorage.getItem(TOKEN_KEY);
		this.isHydrated = true;
	}

	async login(credentials: { username: string; password: string }) {
		const { token } = await loginAdmin(credentials);
		this.token = token;
		if (browser) {
			localStorage.setItem(TOKEN_KEY, token);
		}
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
		if (browser) {
			localStorage.removeItem(TOKEN_KEY);
		}
	}
}

export const authState = new AuthState();
