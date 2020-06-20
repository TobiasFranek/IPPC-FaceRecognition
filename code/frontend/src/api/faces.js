export default {

  async getUnkown() {
    return (await fetch(`${process.env.REACT_APP_API_URL}/faces?known=0`)).json()
  },
  async getKnown() {
    return (await fetch(`${process.env.REACT_APP_API_URL}/faces?known=1`)).json()
  },
  async deleteFace(id) {
    return fetch(`${process.env.REACT_APP_API_URL}/faces/${id}`, {
      method: 'DELETE'
    })
  },
  async rememberFace(id, name) {
    const formData = new FormData();
    formData.append('name', name)
    return fetch(`${process.env.REACT_APP_API_URL}/remember/${id}`, {
      method: 'POST',
      body: formData
    })
  }
}