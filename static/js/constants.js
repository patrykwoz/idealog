const pathname = window.location.pathname;
const segments = pathname.split('/');

let graphUrl;

if (segments.length > 2) {
    const knowledgeBaseId = segments.pop();
    graphUrl = `/api/knowledge-bases/${knowledgeBaseId}`;
} else {
    graphUrl = '/api/knowledge-bases?content=latest';
}
