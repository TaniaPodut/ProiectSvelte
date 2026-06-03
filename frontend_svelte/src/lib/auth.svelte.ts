import { browser } from '$app/environment';
import { fetchCurrentUser, loginStaff, logoutStaff } from '$lib/api';
import type { LoginRequestPayload, User } from '$lib/types';

const SESSION_STORAGE_KEY = 'webtania_session_token';

class AuthState {
	sessionToken = $state<string | null>(null);
	currentUser = $state<User | null>(null);
	isHydrated = $state(false);
	isLoading = $state(false);

	async hydrate() {
		if (!browser || this.isHydrated) return;

		const token = localStorage.getItem(SESSION_STORAGE_KEY);
		if (token) {
			try {
				this.sessionToken = token;
				this.currentUser = await fetchCurrentUser(token);
			} catch {
				this.logout();
			}
		}
		this.isHydrated = true;
	}

	async login(payload: LoginRequestPayload): Promise<User> {
		this.isLoading = true;
		try {
			const response = await loginStaff(payload);
			this.sessionToken = response.session_token;
			this.currentUser = response.user;
			if (browser) {
				localStorage.setItem(SESSION_STORAGE_KEY, response.session_token);
			}
			return response.user;
		} finally {
			this.isLoading = false;
		}
	}

	async logout() {
		if (this.sessionToken) {
			try {
				await logoutStaff(this.sessionToken);
			} catch {
				// Ignore logout errors
			}
		}
		this.sessionToken = null;
		this.currentUser = null;
		if (browser) {
			localStorage.removeItem(SESSION_STORAGE_KEY);
		}
	}
}

export const authState = new AuthState();
