async function setReaction(reaction, articleId) {
    try {
        const res = await fetch(`/article/${reaction}/${articleId}`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ reaction })
        });

        const data = await res.json();
        
        if (data.warning !== undefined)  {
            return
        }
        document.getElementById('quantityLike').textContent = data.like
        document.getElementById('quantityDislike').textContent = data.dislike
    } catch (error) {
        console.error('Failed to set reaction', error)
    }
}