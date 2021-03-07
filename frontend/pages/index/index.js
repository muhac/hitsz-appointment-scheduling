// index.js
// 获取应用实例
const app = getApp()

Page({
   data: {
      mask_show: true,
      motto: 'Hello World',
      userInfo: {},
      hasUserInfo: false,
      canIUse: wx.canIUse('button.open-type.getUserInfo'),
      code: [],
      banner: 1,
   },
   // 事件处理函数
   onLoad() {
      var i = Math.ceil(Math.random() * 7)
      this.setData({
         banner: i
      })
   },
   changebanner() {
      var i = this.data.banner;
      i = i + 1;
      if (i > 7) {
         i = 1;
      }
      this.setData({
         banner: i
      })
   },
   bindViewTap() {
      wx.navigateTo({
         url: '../logs/logs'
      })
   },
   gotoAdmin() {
      wx.navigateTo({
         url: '../admin_verify/admin_verify'
      })
   },
   gotoBook() {
      wx.navigateTo({
         url: '../book/book'
      })
   },
   gotomyBooks() {
      wx.navigateTo({
         url: '../mybooks/mybooks'
      })
   },
   /**
    * 用户点击右上角分享
    */
   onShareAppMessage: function () {

   },
})