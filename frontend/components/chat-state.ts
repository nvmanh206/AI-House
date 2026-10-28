export function chatStorageKey(userId: string, householdId: string) {
    return `nha_minh_ai_chat_v2_${userId}_${householdId}`;
}

export function persistableMessages(messages: Record<string, any>[]) {
    return messages.slice(-20).map(({ imagePreview, image_base64, ...message }) => message);
}
