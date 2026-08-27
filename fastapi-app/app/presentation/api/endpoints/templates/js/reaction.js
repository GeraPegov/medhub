async function setReaction(reaction, articleId) {
    if (reaction !== "like" && reaction !== "dislike") {
        return
    }

    const csrfToken = document
        .querySelector('meta[name="csrf-token"]')
        ?.getAttribute("content")

    try {
        const res = await fetch(`/article/${reaction}/${articleId}`, {
            method: 'POST',
            headers: {
                "Accept": "application/json",
                "X-CSRF-Token": csrfToken ?? "",
            },
        });

        const data = await res.json();

        if (!res.ok) {
            alert(data.error ?? "Не удалось поставить реакцию")
            return
        }

        document.getElementById('quantityLike').textContent = data["likes"]
        document.getElementById('quantityDislike').textContent = data["dislikes"]
    } catch (error) {
        console.error('Failed to set reaction', error)
    }
}
