<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { authState } from '$lib/auth.svelte';

	let username = $state('');
	let password = $state('');
	let errorMessage = $state('');
	let isLoading = $state(false);

	onMount(() => {
		authState.hydrate();
		if (authState.token) {
			goto('/admin');
		}
	});

	async function handleSubmit(event: SubmitEvent) {
		event.preventDefault();
		errorMessage = '';
		isLoading = true;

		try {
			await authState.login({ username, password });
			await goto('/admin');
		} catch (error: any) {
			errorMessage = error.message || 'Eroare la autentificare.';
		} finally {
			isLoading = false;
		}
	}
</script>

<svelte:head>
	<title>Autentificare Admin - Webtania</title>
</svelte:head>

<section class="login-shell">
	<div class="login-card">
		<p class="eyebrow">Acces Administrativ</p>
		<h1>Autentificare</h1>
		<p class="intro">
			Gestionați catalogul de produse, comenzile și mesajele clienților.
		</p>

		<form class="login-form" onsubmit={handleSubmit}>
			<label>
				<span>Utilizator</span>
				<input bind:value={username} type="text" required />
			</label>

			<label>
				<span>Parolă</span>
				<input
					bind:value={password}
					type="password"
					required
				/>
			</label>

			{#if errorMessage}
				<p class="message error">{errorMessage}</p>
			{/if}

			<button type="submit" disabled={isLoading}>
				{isLoading ? 'Se autentifică...' : 'Autentificare'}
			</button>
		</form>

		<a class="back-link" href="/">Înapoi la site</a>
	</div>
</section>

<style>
	.login-shell {
		min-height: 100vh;
		display: grid;
		place-items: center;
		padding: 32px 20px;
		background: #f3f1ea;
	}
	.login-card {
		width: min(100%, 400px);
		padding: 32px;
		border-radius: 16px;
		background: white;
		box-shadow: 0 10px 30px rgba(0,0,0,0.05);
	}
	.eyebrow { font-weight: bold; color: #2e6e5f; margin-bottom: 8px; }
	h1 { margin: 0 0 16px; }
	.login-form { display: grid; gap: 16px; }
	label { display: grid; gap: 6px; font-weight: bold; }
	input { padding: 12px; border: 1px solid #ddd; border-radius: 8px; }
	button { background: #2e6e5f; color: white; border: none; padding: 14px; border-radius: 8px; font-weight: bold; cursor: pointer; }
	button:disabled { opacity: 0.7; }
	.error { color: #d32f2f; font-size: 0.9rem; }
	.back-link { display: block; margin-top: 20px; text-align: center; color: #666; text-decoration: none; }
</style>
