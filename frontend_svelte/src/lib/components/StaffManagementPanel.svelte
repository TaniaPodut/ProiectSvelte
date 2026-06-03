<script lang="ts">
	import { onMount } from 'svelte';
	import { createStaffUser, fetchStaffUsers, getApiErrorMessage, updateStaffUser } from '$lib/api';
	import { authState } from '$lib/auth.svelte';
	import type { StaffUserCreatePayload, StaffUserUpdatePayload, User, UserRole } from '$lib/types';

	type StaffDraft = {
		display_name: string;
		role: UserRole;
		is_active: boolean;
	};

	let isLoadingStaffUsers = $state(true);
	let isCreatingStaffUser = $state(false);
	let updatingStaffUserId = $state<number | null>(null);
	let staffUsers = $state<User[]>([]);
	let staffDrafts = $state<Record<number, StaffDraft>>({});
	let staffMessage = $state('');
	let staffMessageType = $state<'success' | 'error' | ''>('');
	let newDisplayName = $state('');
	let newEmail = $state('');
	let newPassword = $state('');
	let newRole = $state<UserRole>('manager');

	function sortStaffUsers(users: User[]): User[] {
		return [...users].sort((left, right) => left.id - right.id);
	}

	function setStaffMessage(message: string, type: 'success' | 'error'): void {
		staffMessage = message;
		staffMessageType = type;
	}

	function resetStaffForm(): void {
		newDisplayName = '';
		newEmail = '';
		newPassword = '';
		newRole = 'manager';
	}

	function syncStaffDrafts(users: User[]): void {
		staffDrafts = Object.fromEntries(
			users.map((user) => [
				user.id,
				{
					display_name: user.display_name,
					role: user.role,
					is_active: user.is_active
				}
			])
		);
	}

	function updateStaffDraft(userId: number, patch: Partial<StaffDraft>): void {
		staffDrafts = {
			...staffDrafts,
			[userId]: {
				...(staffDrafts[userId] ?? {
					display_name: '',
					role: 'manager',
					is_active: true
				}),
				...patch
			}
		};
	}

	function isCurrentSignedInAdmin(user: User): boolean {
		return authState.currentUser?.id === user.id;
	}

	async function loadStaffUsers(): Promise<void> {
		if (!authState.sessionToken) {
			return;
		}

		isLoadingStaffUsers = true;
		staffMessage = '';
		staffMessageType = '';

		try {
			const users = sortStaffUsers(await fetchStaffUsers(authState.sessionToken));
			staffUsers = users;
			syncStaffDrafts(users);
		} catch (error) {
			staffUsers = [];
			setStaffMessage(
				getApiErrorMessage(error, 'Nu s-au putut încărca conturile staff-ului momentan.'),
				'error'
			);
		} finally {
			isLoadingStaffUsers = false;
		}
	}

	function buildCreatePayload(): StaffUserCreatePayload {
		if (!newDisplayName.trim() || !newEmail.trim() || !newPassword.trim()) {
			throw new Error('Te rugăm să completezi toate câmpurile contului.');
		}

		if (newPassword.trim().length < 8) {
			throw new Error('Parola trebuie să aibă cel puțin 8 caractere.');
		}

		return {
			display_name: newDisplayName.trim(),
			email: newEmail.trim(),
			password: newPassword,
			role: newRole
		};
	}

	onMount(() => {
		void loadStaffUsers();
	});

	async function handleCreateStaffUser(event: SubmitEvent): Promise<void> {
		event.preventDefault();

		if (!authState.sessionToken) {
			setStaffMessage('Sesiunea ta nu mai este activă. Te rugăm să te autentifici din nou.', 'error');
			return;
		}

		isCreatingStaffUser = true;
		staffMessage = '';
		staffMessageType = '';

		try {
			const createdUser = await createStaffUser(authState.sessionToken, buildCreatePayload());
			const nextUsers = sortStaffUsers([...staffUsers, createdUser]);
			staffUsers = nextUsers;
			syncStaffDrafts(nextUsers);
			resetStaffForm();
			setStaffMessage(`Am creat contul de staff pentru ${createdUser.display_name}.`, 'success');
		} catch (error) {
			const fallbackMessage =
				error instanceof Error ? error.message : 'Nu s-a putut crea contul momentan.';
			setStaffMessage(getApiErrorMessage(error, fallbackMessage), 'error');
		} finally {
			isCreatingStaffUser = false;
		}
	}

	async function handleSaveStaffUser(user: User): Promise<void> {
		if (!authState.sessionToken) {
			setStaffMessage('Sesiunea ta nu mai este activă. Te rugăm să te autentifici din nou.', 'error');
			return;
		}

		const draft = staffDrafts[user.id];
		if (!draft) {
			return;
		}

		if (!draft.display_name.trim()) {
			setStaffMessage('Numele afișat nu poate fi gol.', 'error');
			return;
		}

		if (isCurrentSignedInAdmin(user)) {
			if (!draft.is_active) {
				setStaffMessage('Contul de admin autentificat trebuie să rămână activ.', 'error');
				return;
			}

			if (draft.role !== 'admin') {
				setStaffMessage('Contul de admin autentificat trebuie să păstreze accesul de admin.', 'error');
				return;
			}
		}

		const payload: StaffUserUpdatePayload = {
			display_name: draft.display_name.trim(),
			role: draft.role,
			is_active: draft.is_active
		};

		updatingStaffUserId = user.id;
		staffMessage = '';
		staffMessageType = '';

		try {
			const updatedUser = await updateStaffUser(authState.sessionToken, user.id, payload);
			const nextUsers = sortStaffUsers(
				staffUsers.map((staffUser) => (staffUser.id === user.id ? updatedUser : staffUser))
			);
			staffUsers = nextUsers;
			syncStaffDrafts(nextUsers);

			if (authState.currentUser?.id === updatedUser.id) {
				authState.currentUser = updatedUser;
			}

			setStaffMessage(`Am actualizat contul lui ${updatedUser.display_name}.`, 'success');
		} catch (error) {
			setStaffMessage(
				getApiErrorMessage(error, 'Nu s-a putut actualiza contul momentan.'),
				'error'
			);
		} finally {
			updatingStaffUserId = null;
		}
	}
</script>

<section class="staff-layout">
	<section class="staff-panel">
		<div class="panel-header">
			<div>
				<p class="eyebrow">Conturi</p>
				<h2>Creează un cont de staff</h2>
			</div>
			<p class="panel-count">{staffUsers.length} utilizatori staff</p>
		</div>

		<form class="staff-form" onsubmit={handleCreateStaffUser}>
			<label>
				<span>Nume afișat</span>
				<input bind:value={newDisplayName} type="text" required />
			</label>

			<label>
				<span>Email</span>
				<input bind:value={newEmail} type="email" required />
			</label>

			<label>
				<span>Parolă</span>
				<input bind:value={newPassword} type="password" minlength="8" required />
			</label>

			<label>
				<span>Rol</span>
				<select bind:value={newRole}>
					<option value="manager">Manager</option>
					<option value="admin">Admin</option>
				</select>
			</label>

			<div class="form-actions form-span-2">
				<button type="submit" disabled={isCreatingStaffUser}>
					{isCreatingStaffUser ? 'Se creează...' : 'Creează cont staff'}
				</button>
				<button
					class="secondary"
					type="button"
					onclick={resetStaffForm}
					disabled={isCreatingStaffUser}
				>
					Resetează
				</button>
			</div>
		</form>
	</section>

	<section class="staff-panel">
		<div class="panel-header">
			<div>
				<p class="eyebrow">Echipă</p>
				<h2>Gestionează accesul staff-ului</h2>
			</div>
			<p class="panel-note">Actualizează numele, rolurile și statusul conturilor.</p>
		</div>

		{#if staffMessage}
			<p class={`message ${staffMessageType}`}>{staffMessage}</p>
		{/if}

		{#if isLoadingStaffUsers}
			<p class="loading-copy">Se încarcă conturile...</p>
		{:else if staffUsers.length === 0}
			<p class="empty-state">Nu există încă conturi de staff disponibile.</p>
		{:else}
			<div class="staff-list">
				{#each staffUsers as user (user.id)}
					<article class="staff-card">
						<div class="staff-card-top">
							<div>
								<p class="staff-email">{user.email}</p>
								<h3>{staffDrafts[user.id]?.display_name ?? user.display_name}</h3>
							</div>
							<div class="badge-row">
								<span
									class={`badge ${(staffDrafts[user.id]?.is_active ?? user.is_active) ? 'active-badge' : 'inactive-badge'}`}
								>
									{(staffDrafts[user.id]?.is_active ?? user.is_active) ? 'Activ' : 'Inactiv'}
								</span>
								<span class="badge role-badge">{staffDrafts[user.id]?.role ?? user.role}</span>
							</div>
						</div>

						<div class="staff-controls">
							<label>
								<span>Nume afișat</span>
								<input
									value={staffDrafts[user.id]?.display_name ?? user.display_name}
									oninput={(event) =>
										updateStaffDraft(user.id, {
											display_name: (event.currentTarget as HTMLInputElement).value
										})}
								/>
							</label>

							<label>
								<span>Rol</span>
								<select
									value={staffDrafts[user.id]?.role ?? user.role}
									onchange={(event) =>
										updateStaffDraft(user.id, {
											role: (event.currentTarget as HTMLSelectElement).value as UserRole
										})}
									disabled={isCurrentSignedInAdmin(user)}
								>
									<option value="manager">Manager</option>
									<option value="admin">Admin</option>
								</select>
							</label>

							<label class="toggle-field">
								<input
									type="checkbox"
									checked={staffDrafts[user.id]?.is_active ?? user.is_active}
									onchange={(event) =>
										updateStaffDraft(user.id, {
											is_active: (event.currentTarget as HTMLInputElement).checked
										})}
									disabled={isCurrentSignedInAdmin(user)}
								/>
								<span>Cont activ</span>
							</label>
						</div>

						<div class="card-actions">
							<button
								type="button"
								onclick={() => handleSaveStaffUser(user)}
								disabled={updatingStaffUserId === user.id}
							>
								{updatingStaffUserId === user.id ? 'Se salvează...' : 'Salvează modificările'}
							</button>

							{#if isCurrentSignedInAdmin(user)}
								<p class="inline-note">
									Contul de admin autentificat trebuie să rămână activ și să păstreze accesul de admin.
								</p>
							{/if}
						</div>
					</article>
				{/each}
			</div>
		{/if}
	</section>
</section>

<style>
	.staff-layout {
		display: grid;
		gap: 20px;
	}

	.staff-panel {
		padding: 32px;
		border-radius: 24px;
		background: rgba(255, 250, 245, 0.95);
		box-shadow: 0 24px 60px rgba(31, 19, 15, 0.2);
	}

	.panel-header {
		display: flex;
		justify-content: space-between;
		gap: 16px;
		align-items: end;
		margin-bottom: 20px;
	}

	.eyebrow {
		margin: 0 0 10px;
		font-size: 0.8rem;
		font-weight: 800;
		letter-spacing: 0.16em;
		text-transform: uppercase;
		color: #8a4b08;
	}

	h2,
	h3,
	p {
		margin: 0;
	}

	h2,
	h3 {
		font-family: 'Playfair Display', serif;
		color: #2d1b16;
	}

	.panel-count,
	.panel-note,
	.loading-copy,
	.empty-state,
	.staff-email,
	.inline-note {
		color: #5a3e34;
	}

	.staff-form,
	.staff-controls {
		display: grid;
		grid-template-columns: repeat(2, minmax(0, 1fr));
		gap: 16px;
	}

	label {
		display: grid;
		gap: 8px;
		font-weight: 700;
		color: #5a3e34;
	}

	span {
		font-size: 0.95rem;
	}

	input,
	select {
		border: 1px solid rgba(45, 27, 22, 0.14);
		border-radius: 16px;
		padding: 12px 14px;
		font: inherit;
		background: #fffdfb;
		color: #2d1b16;
	}

	.form-span-2 {
		grid-column: 1 / -1;
	}

	.form-actions,
	.card-actions,
	.badge-row {
		display: flex;
		gap: 12px;
		flex-wrap: wrap;
	}

	button {
		border: none;
		border-radius: 999px;
		padding: 12px 18px;
		font: inherit;
		font-weight: 800;
		background: #8a4b08;
		color: #fffaf5;
		cursor: pointer;
	}

	button:disabled {
		opacity: 0.6;
		cursor: wait;
	}

	.secondary {
		background: #ead8ca;
		color: #5a3e34;
	}

	.message {
		margin-bottom: 18px;
		padding: 12px 14px;
		border-radius: 14px;
		font-weight: 700;
	}

	.message.success {
		background: rgba(59, 122, 90, 0.14);
		color: #295940;
	}

	.message.error {
		background: rgba(143, 44, 44, 0.12);
		color: #8f2c2c;
	}

	.staff-list {
		display: grid;
		gap: 16px;
	}

	.staff-card {
		padding: 22px;
		border-radius: 22px;
		background: linear-gradient(180deg, rgba(255, 247, 241, 0.96), rgba(255, 255, 255, 0.98));
		border: 1px solid rgba(45, 27, 22, 0.08);
		box-shadow: 0 18px 40px rgba(45, 27, 22, 0.08);
		display: grid;
		gap: 16px;
	}

	.staff-card-top {
		display: flex;
		justify-content: space-between;
		gap: 16px;
		align-items: start;
	}

	.staff-email {
		font-size: 0.9rem;
	}

	.badge {
		display: inline-flex;
		align-items: center;
		padding: 7px 10px;
		border-radius: 999px;
		font-size: 0.85rem;
		font-weight: 700;
		text-transform: capitalize;
	}

	.active-badge {
		background: rgba(59, 122, 90, 0.14);
		color: #295940;
	}

	.inactive-badge {
		background: rgba(143, 44, 44, 0.12);
		color: #8f2c2c;
	}

	.role-badge {
		background: rgba(138, 75, 8, 0.1);
		color: #8a4b08;
	}

	.toggle-field {
		display: flex;
		align-items: center;
		gap: 12px;
	}

	.toggle-field input {
		width: 18px;
		height: 18px;
		padding: 0;
		margin: 0;
	}

	.inline-note {
		font-size: 0.92rem;
		line-height: 1.5;
	}

	@media (max-width: 720px) {
		.staff-panel {
			padding: 24px;
		}

		.panel-header,
		.staff-card-top {
			flex-direction: column;
			align-items: start;
		}

		.staff-form,
		.staff-controls {
			grid-template-columns: 1fr;
		}

		.form-span-2 {
			grid-column: auto;
		}

		.toggle-field {
			align-items: start;
		}
	}
</style>
