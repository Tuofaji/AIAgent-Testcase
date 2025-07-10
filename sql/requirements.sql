CREATE TABLE test_requirements (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    requirements TEXT NOT NULL,
    tag INTEGER DEFAULT 0,
    date TEXT NOT NULL,
    submitter TEXT NOT NULL,
    importance TEXT NOT NULL,
    moduleName TEXT NOT NULL
);
-- INSERT INTO test_requirements (requirements, tag, date, submitter) VALUES ('验证用户注册功能是否正常', 0, '2024-09-15', '田老师');
-- INSERT INTO test_requirements (requirements, tag, date, submitter) VALUES ('验证用户登录功能是否正常', 1, '2024-09-16', '助教小姐姐');
-- INSERT INTO test_requirements (requirements, tag, date, submitter) VALUES ('验证用户密码重置功能是否正常', 0, '2024-09-17', '但问智能');
-- INSERT INTO test_requirements (requirements, tag, date, submitter) VALUES ('验证用户注销功能是否正常', 1, '2024-09-18', '田老师');
-- INSERT INTO test_requirements (requirements, tag, date, submitter) VALUES ('验证用户个人资料编辑功能是否正常', 0, '2024-09-19', '助教小姐姐');
-- INSERT INTO test_requirements (requirements, tag, date, submitter) VALUES ('验证用户收货地址添加功能是否正常', 1, '2024-09-20', '但问智能');
-- INSERT INTO test_requirements (requirements, tag, date, submitter) VALUES ('验证用户收货地址编辑功能是否正常', 0, '2024-09-21', '田老师');
-- INSERT INTO test_requirements (requirements, tag, date, submitter) VALUES ('验证用户收货地址删除功能是否正常', 1, '2024-09-22', '助教小姐姐');
-- INSERT INTO test_requirements (requirements, tag, date, submitter) VALUES ('验证商品搜索功能是否正常', 0, '2024-09-23', '但问智能');
-- INSERT INTO test_requirements (requirements, tag, date, submitter) VALUES ('验证商品分类浏览功能是否正常', 1, '2024-09-24', '田老师');
-- INSERT INTO test_requirements (requirements, tag, date, submitter) VALUES ('验证商品详情页显示是否正常', 0, '2024-09-25', '助教小姐姐');
-- INSERT INTO test_requirements (requirements, tag, date, submitter) VALUES ('验证商品加入购物车功能是否正常', 1, '2024-09-26', '但问智能');
-- INSERT INTO test_requirements (requirements, tag, date, submitter) VALUES ('验证购物车商品数量修改功能是否正常', 0, '2024-09-27', '田老师');
-- INSERT INTO test_requirements (requirements, tag, date, submitter) VALUES ('验证购物车商品删除功能是否正常', 1, '2024-09-28', '助教小姐姐');
-- INSERT INTO test_requirements (requirements, tag, date, submitter) VALUES ('验证购物车结算功能是否正常', 0, '2024-09-29', '但问智能');
-- INSERT INTO test_requirements (requirements, tag, date, submitter) VALUES ('验证订单创建功能是否正常', 1, '2024-09-30', '田老师');
-- INSERT INTO test_requirements (requirements, tag, date, submitter) VALUES ('验证订单支付功能是否正常', 0, '2024-10-01', '助教小姐姐');
-- INSERT INTO test_requirements (requirements, tag, date, submitter) VALUES ('验证订单取消功能是否正常', 1, '2024-10-02', '但问智能');
-- INSERT INTO test_requirements (requirements, tag, date, submitter) VALUES ('验证订单详情页显示是否正常', 0, '2024-10-03', '田老师');
-- INSERT INTO test_requirements (requirements, tag, date, submitter) VALUES ('验证订单物流信息查询功能是否正常', 1, '2024-10-04', '助教小姐姐');
-- INSERT INTO test_requirements (requirements, tag, date, submitter) VALUES ('验证优惠券添加功能是否正常', 0, '2024-10-05', '但问智能');
-- INSERT INTO test_requirements (requirements, tag, date, submitter) VALUES ('验证优惠券使用功能是否正常', 1, '2024-10-06', '田老师');
-- INSERT INTO test_requirements (requirements, tag, date, submitter) VALUES ('验证优惠券过期功能是否正常', 0, '2024-10-07', '助教小姐姐');
-- INSERT INTO test_requirements (requirements, tag, date, submitter) VALUES ('验证积分获取功能是否正常', 1, '2024-10-08', '但问智能');
-- INSERT INTO test_requirements (requirements, tag, date, submitter) VALUES ('验证积分兑换功能是否正常', 0, '2024-10-09', '田老师');
-- INSERT INTO test_requirements (requirements, tag, date, submitter) VALUES ('验证商品评价功能是否正常', 1, '2024-10-10', '助教小姐姐');
-- INSERT INTO test_requirements (requirements, tag, date, submitter) VALUES ('验证商品评价显示功能是否正常', 0, '2024-10-11', '但问智能');
-- INSERT INTO test_requirements (requirements, tag, date, submitter) VALUES ('验证商品评价修改功能是否正常', 1, '2024-10-12', '田老师');
-- INSERT INTO test_requirements (requirements, tag, date, submitter) VALUES ('验证商品评价删除功能是否正常', 0, '2024-10-13', '助教小姐姐');
-- INSERT INTO test_requirements (requirements, tag, date, submitter) VALUES ('验证商品库存显示是否正常', 1, '2024-10-14', '但问智能');
-- INSERT INTO test_requirements (requirements, tag, date, submitter) VALUES ('验证商品库存不足提示功能是否正常', 0, '2024-10-15', '田老师');
-- INSERT INTO test_requirements (requirements, tag, date, submitter) VALUES ('验证商品上架功能是否正常', 1, '2024-10-16', '助教小姐姐');
-- INSERT INTO test_requirements (requirements, tag, date, submitter) VALUES ('验证商品下架功能是否正常', 0, '2024-10-17', '但问智能');
-- INSERT INTO test_requirements (requirements, tag, date, submitter) VALUES ('验证商品图片显示是否正常', 1, '2024-10-18', '田老师');
-- INSERT INTO test_requirements (requirements, tag, date, submitter) VALUES ('验证商品描述信息显示是否正常', 0, '2024-10-19', '助教小姐姐');
-- INSERT INTO test_requirements (requirements, tag, date, submitter) VALUES ('验证商品价格显示是否正常', 1, '2024-10-20', '但问智能');
-- INSERT INTO test_requirements (requirements, tag, date, submitter) VALUES ('验证商品促销信息显示是否正常', 0, '2024-10-21', '田老师');
-- INSERT INTO test_requirements (requirements, tag, date, submitter) VALUES ('验证商品多规格选择功能是否正常', 1, '2024-10-22', '助教小姐姐');
-- INSERT INTO test_requirements (requirements, tag, date, submitter) VALUES ('验证商品多规格价格计算功能是否正常', 0, '2024-10-23', '但问智能');
-- INSERT INTO test_requirements (requirements, tag, date, submitter) VALUES ('验证商品多规格库存显示是否正常', 1, '2024-10-24', '田老师');
-- INSERT INTO test_requirements (requirements, tag, date, submitter) VALUES ('验证商品多规格加入购物车功能是否正常', 0, '2024-10-25', '助教小姐姐');
-- INSERT INTO test_requirements (requirements, tag, date, submitter) VALUES ('验证商品多规格结算功能是否正常', 1, '2024-10-26', '但问智能');
-- INSERT INTO test_requirements (requirements, tag, date, submitter) VALUES ('验证商品多规格订单创建功能是否正常', 0, '2024-10-27', '田老师');
-- INSERT INTO test_requirements (requirements, tag, date, submitter) VALUES ('验证商品多规格订单支付功能是否正常', 1, '2024-10-28', '助教小姐姐');
-- INSERT INTO test_requirements (requirements, tag, date, submitter) VALUES ('验证商品多规格订单取消功能是否正常', 0, '2024-10-29', '但问智能');
-- INSERT INTO test_requirements (requirements, tag, date, submitter) VALUES ('验证商品多规格订单详情页显示是否正常', 1, '2024-10-30', '田老师');
-- INSERT INTO test_requirements (requirements, tag, date, submitter) VALUES ('验证商品多规格订单物流信息查询功能是否正常', 0, '2024-10-31', '助教小姐姐');
-- INSERT INTO test_requirements (requirements, tag, date, submitter) VALUES ('验证商品多规格评价功能是否正常', 1, '2024-11-01', '但问智能');
-- INSERT INTO test_requirements (requirements, tag, date, submitter) VALUES ('验证商品多规格评价显示功能是否正常', 0, '2024-11-02', '田老师');
-- INSERT INTO test_requirements (requirements, tag, date, submitter) VALUES ('验证商品多规格评价修改功能是否正常', 1, '2024-11-03', '助教小姐姐');
-- INSERT INTO test_requirements (requirements, tag, date, submitter) VALUES ('验证商品多规格评价删除功能是否正常', 0, '2024-11-04', '但问智能');
-- INSERT INTO test_requirements (requirements, tag, date, submitter) VALUES ('验证商品多规格库存显示是否正常', 1, '2024-11-05', '田老师');
-- INSERT INTO test_requirements (requirements, tag, date, submitter) VALUES ('验证商品多规格库存不足提示功能是否正常', 0, '2024-11-06', '助教小姐姐');
-- INSERT INTO test_requirements (requirements, tag, date, submitter) VALUES ('验证商品多规格上架功能是否正常', 1, '2024-11-07', '但问智能');
-- INSERT INTO test_requirements (requirements, tag, date, submitter) VALUES ('验证商品多规格下架功能是否正常', 0, '2024-11-08', '田老师');
-- INSERT INTO test_requirements (requirements, tag, date, submitter) VALUES ('验证商品多规格图片显示是否正常', 1, '2024-11-09', '助教小姐姐');
-- INSERT INTO test_requirements (requirements, tag, date, submitter) VALUES ('验证商品多规格描述信息显示是否正常', 0, '2024-11-10', '但问智能');
-- INSERT INTO test_requirements (requirements, tag, date, submitter) VALUES ('验证商品多规格价格显示是否正常', 1, '2024-11-11', '田老师');
-- INSERT INTO test_requirements (requirements, tag, date, submitter) VALUES ('验证商品多规格促销信息显示是否正常', 0, '2024-11-12', '助教小姐姐');