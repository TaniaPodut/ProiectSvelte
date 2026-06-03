<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { getOrders, getContactMessages, getApiErrorMessage } from '$lib/api';
	import { authState } from '$lib/auth.svelte';
	import type { Order, ContactPayload } from '$lib/types';

	let isReady = $state(false);
	let isLoading = $state(true);
	let orders = $state<Order[]>([]);
	let messages = $state<ContactPayload[]>([]);
	let pageMessage = $state('');
	let pageMessageType = $state<'success' | 'error' | ''>('');

	async function loadData(): Promise<void> {
		if (!authState.sessionToken) return;

		isLoading = true;
		try {
			const [ordersData, messagesData] = await Promise.all([
				getOrders(authState.sessionToken),
				getContactMessages(authState.sessionToken)
			]);
			orders = ordersData;
			messages = messagesData;
		} catch (error) {
			pageMessage = getApiErrorMessage(error, 'Nu s-au putut încărca datele.');
			pageMessageType = 'error';
		} finally {
			isLoading = false;
		}
	}

	onMount(async () => {
		await authState.hydrate();
		if (!authState.currentUser) {
			await goto('/login');
			return;
		}
		isReady = true;
		await loadData();
	});

	async function handleLogout(): Promise<void> {
		await authState.logout();
		await goto('/login');
	}
</script>

<svelte:head>
	<title>Panou Manager - Webtania</title>
</svelte:head>

<section class="dashboard-shell">
	{#if !isReady}
		<p class="loading-copy">Se încarcă dashboard-ul...</p>
	{:else}
		<div class="dashboard-grid">
			<section class="panel hero-panel">
				<p class="eyebrow">Manager</p>
				<h1>Panou de Control Operativ</h1>
				<p class="intro">
					Bine ai venit, {authState.currentUser?.display_name}. Aici poți monitoriza comenzile clienților și mesajele primite prin formularul de contact.
				</p>
				<div class="actions">
					{#if authState.currentUser?.role === 'admin'}
						<a href="/admin">Panou Admin (Produse)</a>
					{/if}
					<button type="button" onclick={handleLogout}>Deconectare</button>
				</div>
			</section>

			{#if pageMessage}
				<p class={`message ${pageMessageType}`}>{pageMessage}</p>
			{/if}

			<section class="panel orders-panel">
				<div class="panel-header">
					<h2>Comenzi clienți</h2>
					<p class="count">{orders.length} comenzi</p>
				</div>

				{#if isLoading}
					<p>Se încarcă...</p>
				{:else if orders.length === 0}
					<p class="empty-state">Nu există comenzi momentan.</p>
				{:else}
					<div class="tabel-container">
						<table>
							<thead>
								<tr>
									<th>ID</th>
									<th>Client</th>
									<th>Produs</th>
									<th>Adresă</th>
									<th>Status</th>
								</tr>
							</thead>
							<tbody>
								{#each orders as order}
									<tr>
										<td>#{order.id}</td>
										<td>{order.contact_name}<br/><small>{order.contact_email}</small></td>
										<td>ID {order.produs_id} (x{order.quantity})</td>
										<td>{order.delivery_address}</td>
										<td><span class="badge">{order.status}</span></td>
									</tr>
								{/each}
							</tbody>
						</table>
					</div>
				{/if}
			</section>

			<section class="panel messages-panel">
				<div class="panel-header">
					<h2>Mesaje de contact</h2>
					<p class="count">{messages.length} mesaje</p>
				</div>

				{#if isLoading}
					<p>Se încarcă...</p>
				{:else if messages.length === 0}
					<p class="empty-state">Nu există mesaje noi.</p>
				{:else}
					<div class="messages-list">
						{#each messages as msg}
							<article class="message-card">
								<div class="message-header">
									<strong>{msg.nume}</strong>
									<span>{msg.email} | {msg.telefon}</span>
								</div>
								<p class="message-text">{msg.mesaj}</p>
							</article>
						{/each}
					</div>
				{/if}
			</section>
		</div>
	{/if}
</section>

<style>
	.dashboard-shell {
		min-height: 100vh;
		padding: 24px;
		background: #f3f1ea;
	}
	.dashboard-grid {
		max-width: 1100px;
		margin: 0 auto;
		display: grid;
		gap: 20px;
	}
	.panel {
		padding: 24px;
		background: white;
		border-radius: 16px;
		box-shadow: 0 4px 20px rgba(0,0,0,0.05);
	}
	.hero-panel {
		background: #203b35;
		color: white;
	}
	.eyebrow { font-weight: 800; color: #589981; margin: 0; }
	h1 { margin: 8px 0; }
	.actions { display: flex; gap: 10px; margin-top: 15px; }
	a, button {
		background: #2e6e5f; color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; text-decoration: none; font-weight: bold;
	}
	.panel-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
	.tabel-container { overflow-x: auto; }
	table { width: 100%; border-collapse: collapse; }
	th { text-align: left; padding: 12px; border-bottom: 2px solid #eee; }
	td { padding: 12px; border-bottom: 1px solid #eee; }
	.badge { background: #d5e5e0; padding: 4px 8px; border-radius: 4px; font-size: 0.8rem; }
	.messages-list { display: grid; gap: 10px; }
	.message-card { padding: 15px; background: #f9f9f9; border-radius: 8px; border-left: 4px solid #2e6e5f; }
	.message-header { display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 0.9rem; }
	.message-text { margin: 0; line-height: 1.4; }
</style>
