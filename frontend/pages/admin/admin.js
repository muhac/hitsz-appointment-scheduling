// pages/mybooks/mybooks.js
const app = getApp()
var sliderWidth = 96;
Page({

   /**
    * 页面的初始数据
    */
   data: {
      tabs: ["进行中", "已完成"],
      activeIndex: 0,
      sliderOffset: 0,
      sliderLeft: 0,
      reservations: [],
      tickets: [],
      dialogShow: false,
      dialogContent: [],
      buttons: [{
         text: '取消'
      }, {
         text: '关闭 '
      }],
      buttons_del: [{
         text: '取消'
      }, {
         text: '确定'
      }],
      ticket_chosen: [],
   },

   /**
    * 生命周期函数--监听页面加载
    */
   onLoad: function (options) {
      var that = this;
      var tag = this.data.activeIndex == 0 ? "open" : "closed";
      wx.showLoading({
         title: "获取数据中",
         mask: true
      })
      console.log(app.globalData.admin_password)
      wx.request({
         url: 'https://www.bugstop.site/plan/list/',
         headers: {
            'Content-Type': 'application/json'
         },
         data: {
            user: app.globalData.admin_password,
            tag: tag
         },
         method: "POST",
         success(res) {
            console.log(res.data)
            wx.hideLoading();
            //将获取到的json数据，存在名字叫list的这个数组中
            if (res.data.statusCode == 200) {
               that.setData({
                  reservations: res.data.reservations,
                  tickets: res.data.tickets,
                  //res代表success函数的事件对，data是固定的，list是数组
               })
            } else {
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
            }
            ;
         },
         fail() {
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

   closeonclick: function (e) {
      console.log(e)
      this.setData({
         dialogShow: true,
         ticket_chosen: e.currentTarget.dataset.value
      })
   },

   delonclick: function (e) {
      console.log(e)
      this.setData({
         dialogShow_del: true,
         ticket_chosen: e.currentTarget.dataset.value
      })
   },

   tapDialogButton: function (e) {
      var that = this
      console.log(e)
      this.setData({
         dialogShow: false,
      })
      if (e.detail.index == 1) {
         wx.showLoading({
            title: "关闭中",
            mask: true
         })
         wx.request({
            url: 'https://www.bugstop.site/plan/edit/',
            headers: {
               'Content-Type': 'application/json'
            },
            method: "POST",

            data: {
               user: app.globalData.admin_password,
               tid: that.data.ticket_chosen,
               op: "closed"
            },
            complete() {
               wx.showLoading();
            },
            success(res) {
               console.log(res.data)
               if (res.data.statusCode == 200) {
                  wx.showToast({
                     title: "关闭成功",
                     icon: 'success', //如果要纯文本，不要icon，将值设为'none'
                     mask: true,
                     duration: 2000
                  })
                  that.onLoad();
               } else {
                  wx.showToast({
                     title: "关闭失败",
                     icon: 'error', //如果要纯文本，不要icon，将值设为'none'
                     mask: true,
                     duration: 2000
                  })
               }
            },
            fail() {
               wx.showToast({
                  title: "请求超时",
                  icon: 'error', //如果要纯文本，不要icon，将值设为'none'
                  mask: true,
                  duration: 2000
               })
            }
         })
      }
   },

   tabClick: function (e) {
      var activeIndex = e.currentTarget.id;
      var that = this;
      var tag = activeIndex == 0 ? "open" : "closed";

      console.log(activeIndex)
      console.log(tag)

      wx.showLoading({
         title: "获取数据中",
         mask: true
      })
      wx.request({
         url: 'https://www.bugstop.site/plan/list/',
         headers: {
            'Content-Type': 'application/json'
         },
         data: {
            user: app.globalData.admin_password,
            tag: tag
         },
         method: "POST",
         success(res) {
            console.log(res.data)
            wx.hideLoading();
            //将获取到的json数据，存在名字叫list的这个数组中
            if (res.data.statusCode == 200) {
               that.setData({
                  reservations: res.data.reservations,
                  tickets: res.data.tickets,
                  //res代表success函数的事件对，data是固定的，list是数组
               })
            } else {
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
            }
            ;
         },
         fail() {
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
         },
         complete() {
            that.setData({
               sliderOffset: e.currentTarget.offsetLeft,
               activeIndex: activeIndex
            });
         }
      })
   },

   tapDialogButton_del: function (e) {
      var that = this
      console.log(e)
      this.setData({
         dialogShow_del: false,
      })
      if (e.detail.index == 1) {
         wx.showLoading({
            title: "删除中",
            mask: true
         })
         wx.request({
            url: 'https://www.bugstop.site/plan/edit/',
            headers: {
               'Content-Type': 'application/json'
            },
            method: "POST",
            data: {
               user: app.globalData.admin_password,
               tid: that.data.ticket_chosen,
               op: "cancel"
            },
            complete() {
               wx.showLoading();
            },
            success(res) {
               console.log(res.data)
               if (res.data.statusCode == 200) {
                  wx.showToast({
                     title: "取消成功",
                     icon: 'success', //如果要纯文本，不要icon，将值设为'none'
                     mask: true,
                     duration: 2000
                  })
                  that.onLoad();

               } else {
                  wx.showToast({
                     title: "取消失败",
                     icon: 'error', //如果要纯文本，不要icon，将值设为'none'
                     mask: true,
                     duration: 2000
                  })
               }
            },
            fail() {
               wx.showToast({
                  title: "请求超时",
                  icon: 'error', //如果要纯文本，不要icon，将值设为'none'
                  mask: true,
                  duration: 2000
               })
            }
         })
      }
   }
})