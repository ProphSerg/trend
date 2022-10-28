style = '''
:root {
  --border-width: 2px;
  --border-color: #CED4DA;
  --border: var(--border-width) solid var(--border-color);
}

/* Sticky header */
table {
  border-collapse: separate;
  border-spacing: var(--border-width); /* 1 */
}

thead {
  position: sticky;
  top: var(--border-width); /* 2 */
}

th, td {
  box-shadow: 0 0 0 var(--border-width) var(--border-color); /* 3 */
}

/* Other styles */
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto,
    Oxygen-Sans, Ubuntu, Cantarell, 'Helvetica Neue', Helvetica, Arial,
    sans-serif;
  margin: 0;
}

table {
  //width: 100%;
}

th {
  text-align: left;
  background-color: #f1f3f5;
}

th, td {
  padding: 3px 5px;
}
'''