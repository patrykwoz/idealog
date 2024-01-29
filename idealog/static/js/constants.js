const pathname = window.location.pathname;
const segments = pathname.split('/');

let graphUrl;

if (segments.length > 2) {
    const knowledgeBaseId = segments.pop();
    graphUrl = `/api/knowledge-bases/${knowledgeBaseId}?authorized=authorized`;
} else {
    graphUrl = '/api/knowledge-bases?content=latest&authorized=authorized';
}
