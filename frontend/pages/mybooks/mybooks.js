// pages/mybooks/mybooks.js
const app=getApp()
Page({

  /**
   * 页面的初始数据
   */
  data: {
    inProgress:[],
    tickets:[],
    dialogShow:false,
    dialogContent:[],
    buttons: [{text: '返回'}, {text: '通过'}],
    buttons_del: [{text: '取消'}, {text: '确定'}],
    del_ticket:[],
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {
    var that=this;
    wx.showLoading({
      title: "获取数据中",
      mask: true
  })
    wx.request({
      url: 'https://www.bugstop.site/list/',
      headers: {
          'Content-Type': 'application/json'
      },
      data:{user:app.globalData.wx},
      method:"POST",
      success(res) {
        console.log(res.data)
        wx.hideLoading();
          //将获取到的json数据，存在名字叫list的这个数组中
          if(res.data.statusCode==200){
          that.setData({
              inProgress: res.data.inProgress,
              tickets: res.data.tickets.reverse(), //后端发来的数据是按时间从早到晚顺序的，所以reverse一下
              //res代表success函数的事件对，data是固定的，list是数组
          })}
          else{
            wx.showToast({
              title: "获取数据失败",
              icon: 'error', //如果要纯文本，不要icon，将值设为'none'
              mask: true,
              duration: 3000
          })

          setTimeout(function () {
              wx.reLaunch({
                  url: '/pages/index/index'
              })
          }, 2000)
          };
        },
        fail(){
          wx.hideLoading();
          wx.showToast({
            title: "获取数据超时",
            icon: 'error', //如果要纯文本，不要icon，将值设为'none'
            mask: true,
            duration: 3000
        })
        setTimeout(function () {
          wx.reLaunch({
              url: '/pages/index/index'
          })
      }, 2000)
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

  detailonclick: function(e){
    console.log(e)
    this.setData({
      dialogShow:true,
      dialogContent:e.currentTarget.dataset.value
    })
    
  },

  delonclick: function(e){
    console.log(e)
    this.setData({
      dialogShow_del:true,
      del_ticket:e.currentTarget.dataset.value
    })
    
  },

  tapDialogButton: function(e){
    console.log(e)
    this.setData({
      dialogShow:false,
    })
  },

  tapDialogButton_del: function(e){
    console.log(e)
    this.setData({
      dialogShow_del:false,
    })
  }
})