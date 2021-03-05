// pages/book/book.js
Page({

  /**
   * 页面的初始数据
   */
  data: {



    sexItem: [{
        value: "m",
        name: "男"
      },
      {
        value: "f",
        name: "女"
      }
    ],

  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {
    var that = this
    wx.request({
      url: 'https://www.bugstop.site/available/',
      headers: {
        'Content-Type': 'application/json'
      },
      success(res) {
        //将获取到的json数据，存在名字叫list的这个数组中
        that.setData({
          list: res.data,
          //res代表success函数的事件对，data是固定的，list是数组
        })

      }
    })
  },

  /**
   * 生命周期函数--监听页面初次渲染完成
   */
  onReady: function () {

  },

  /**
   * 生命周期函数--监听页面显示
   */
  onShow: function () {

  },

  /**
   * 生命周期函数--监听页面隐藏
   */
  onHide: function () {

  },

  /**
   * 生命周期函数--监听页面卸载
   */
  onUnload: function () {

  },

  /**
   * 页面相关事件处理函数--监听用户下拉动作
   */
  onPullDownRefresh: function () {

  },

  /**
   * 页面上拉触底事件的处理函数
   */
  onReachBottom: function () {

  },

  /**
   * 用户点击右上角分享
   */
  onShareAppMessage: function () {

  },

  dateChange: function (e) {
    console.log(this)
    console.log(e.detail.value)
    console.log(this.__data__.list.schedule[e.detail.value])
    this.setData({
      hoursItem: this.__data__.list.schedule[e.detail.value],
    })
    console.log(e)
  },

  formSubmit(e) {
    console.log('form发生了submit事件，携带数据为：', e.detail.value)
    wx.request({
      url: 'https://www.bugstop.site/reserve/',
      data: e.detail.value,
      headers: {
        'Content-Type': 'application/json'
      },
      timeout: "10000",
      method: "POST",
      success(res) {
        console.log(res.data)
      }
    })
  },

  formReset: function () {
    console.log('form发生了reset事件')
  }
})