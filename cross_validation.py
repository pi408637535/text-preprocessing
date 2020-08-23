def cross_validation_bagging(model_fn, model_name, train_data, train_label, test_data, batch_size=128, lr=1e-3,
                             num_folds=10, patience=10, seed=1):
    device = 'cuda:0' if torch.cuda.is_available() else 'cpu:0'

    np.random.seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
    else:
        torch.manual_seed(seed)

    # 10折交叉验证
    skf = StratifiedKFold(n_splits=num_folds, shuffle=True, random_state=2018)
    skf_indices = []
    for i, (train_idx, valid_idx) in enumerate(skf.split(np.zeros(len(train_label)), train_label)):
        skf_indices.extend(valid_idx)

    fold_len = len(train_label) // num_folds  # 每一折的数据量
    num_classes = len(set(train_label))  # 类别数
    meta_train = np.zeros((len(train_label), num_classes))  # 在训练集上的预测结果
    meta_test = np.zeros((test_data.shape[0], num_classes))  # 在测试集上的预测结果

    # 将测试数据转换为tensor to(device)
    test_data_tensor = torch.from_numpy(test_data).long().to(device)
    test_label_tensor = torch.zeros(len(test_data)).long().to(device)
    # 对测试数据构建Dataset 和 DataLoader
    test_data_dataset = TensorDataset(test_data_tensor, test_label_tensor)
    test_data_loader = DataLoader(test_data_dataset, batch_size)

    print(f'test_data_dataset & test_data_loader: {torch.cuda.memory_allocated() / 1024 ** 3:.2f}GB')

    for fold in range(num_folds):
        print(f'Loop Begin: {torch.cuda.memory_allocated() / 1024 ** 3:.2f}GB')
        print(f'Processing fold {fold}...')
        fold_start = fold * fold_len
        fold_end = (fold + 1) * fold_len

        # 将训练集划分为训练集、验证集、交叉测试集 fold决定哪个是交叉测试集
        if fold == 0:
            train_indices = skf_indices[fold_len:(num_folds - 1) * fold_len]
            valid_indices = skf_indices[(num_folds - 1) * fold_len:]
        elif fold == num_folds - 1:
            train_indices = skf_indices[:((num_folds - 2) * fold_len)]
            valid_indices = skf_indices[(num_folds - 2) * fold_len:(num_folds - 1) * fold_len]
            fold_end = len(train_label)
        else:
            valid_indices = skf_indices[fold_start - fold_len:fold_start]
            train_indices = skf_indices[:fold_start - fold_len] + skf_indices[fold_end:]
        test_indices = skf_indices[fold_start:fold_end]
        train_x, valid_x, test_x = train_data[train_indices], train_data[valid_indices], train_data[test_indices]
        train_y, valid_y, test_y = train_label[train_indices], train_label[valid_indices], train_label[test_indices]

        train_size = len(train_y)
        valid_size = len(valid_y)
        print(f'# of training samples: {train_size}')
        print(f'# of validation samples: {valid_size}')

        train_x_tensor = torch.from_numpy(train_x).long().to(device)
        train_y_tensor = torch.from_numpy(train_y).long().to(device)
        # train_y_tensor = torch.from_numpy(train_y).float().to(device)
        valid_x_tensor = torch.from_numpy(valid_x).long().to(device)
        valid_y_tensor = torch.from_numpy(valid_y).long().to(device)
        # valid_y_tensor = torch.from_numpy(valid_y).float().to(device)
        test_x_tensor = torch.from_numpy(test_x).long().to(device)
        test_y_tensor = torch.from_numpy(test_y).long().to(device)

        train_dataset = TensorDataset(train_x_tensor, train_y_tensor)
        valid_dataset = TensorDataset(valid_x_tensor, valid_y_tensor)
        test_dataset = TensorDataset(test_x_tensor, test_y_tensor)

        train_loader = DataLoader(train_dataset, batch_size, True)
        valid_loader = DataLoader(valid_dataset, batch_size)
        test_loader = DataLoader(test_dataset, batch_size)

        model = model_fn().to(device)

        criterion = nn.CrossEntropyLoss(size_average=False)
        trainable_params = [p for p in model.parameters() if p.requires_grad]
        optimizer = Adam(trainable_params, lr)
        scheduler = ReduceLROnPlateau(optimizer, 'max', factor=0.5, patience=1, min_lr=5e-6, verbose=True)

        epochs = 1000
        best_epoch = -1
        best_f1 = -1
        best_loss = 1e3
        ckpt_path = None

        for epoch in range(epochs):

            # Early Stopping
            if epoch - best_epoch > patience:
                print(f'No improvement for {patience} epochs, stop training...')
                break

            start = time.time()

            # Training phase
            model.train()
            train_loss = 0.0
            y_true, y_pred = [], []
            for data in train_loader:
                input, y = data
                optimizer.zero_grad()
                outputs = model(input).squeeze()
                loss = criterion(outputs, y)
                y_true.append(y)
                y_pred.append(outputs.cpu().detach().numpy().argmax(axis=1))
                loss.backward()
                clip_grad_norm_(trainable_params, 1.0)
                optimizer.step()
                train_loss += loss.item() / train_size
                del input, y
            y_true = np.concatenate(y_true)
            y_pred = np.concatenate(y_pred)
            train_f1 = f1_score(y_true, y_pred, average='macro')
            del y_pred, y_true

            # Validation phase 每一个epoch结束在验证集上验证
            model.eval()
            valid_loss = 0.0
            pred = []
            with torch.no_grad():
                for data in valid_loader:
                    input, y = data
                    outputs = model(input).squeeze()
                    loss = criterion(outputs, y)
                    pred.append(outputs.cpu().detach().numpy().argmax(axis=1))
                    valid_loss += loss.item() / valid_size
                    del input, y
            valid_y_pred = np.concatenate(pred)
            valid_f1 = f1_score(valid_y, valid_y_pred, average='macro')
            scheduler.step(valid_f1)
            del valid_y_pred

            if valid_f1 > best_f1:  # 保存在验证集上 f1-score最高的一组参数
                # Remove stale checkpoint
                if ckpt_path is not None:
                    os.remove(ckpt_path)
                best_epoch = epoch
                best_f1 = valid_f1
                ckpt_path = f'../../ckpt/{model_name}/{seed}/fold{fold}.ckpt'
                if not os.path.exists(os.path.dirname(ckpt_path)):
                    os.makedirs(os.path.dirname(ckpt_path))
                torch.save(model.state_dict(), ckpt_path)
                elapsed = time.time() - start
                print(f'Epoch {epoch} in {elapsed:.1f}s: saved in {ckpt_path}')
                print(f'    train loss: {train_loss:.4f} valid loss: {valid_loss:.4f} ')
                print(f'    train f1_macro: {train_f1:.4f} valid f1_macro: {valid_f1:.4f}')
            else:
                elapsed = time.time() - start
                print(f'Epoch {epoch} in {elapsed:.1f}s: not improved')
                print(f'    train loss: {train_loss:.4f} valid loss: {valid_loss:.4f}')
                print(f'    train f1_macro: {train_f1:.4f} valid f1_macro: {valid_f1:.4f}')

        # 一次训练结束后 加载当前最好的参数   （10折 有10次训练）
        model.load_state_dict(torch.load(ckpt_path))

        pred = []
        model.eval()
        with torch.no_grad():  # 在交叉测试集上测试
            for data in test_loader:
                input, _ = data
                outputs = model(input).squeeze()
                pred.append(outputs)
                del input
        pred = np.concatenate(pred, axis=0)
        meta_train[test_indices] = softmax(pred)  # 将预测结果先通过softmax 转换为概率分布 在把值赋给完整训练集的相应的位置 10折训练完后 将会得到完整训练集的预测结果
        del pred

        pred = []
        model.eval()
        with torch.no_grad():  # 在测试集上测试
            for data in test_data_loader:
                input, _ = data
                outputs = model(input).squeeze()
                pred.append(outputs)
                del input
        pred = np.concatenate(pred, axis=0)  # 得到在测试集上的预测结果
        meta_test += softmax(pred) / num_folds  # 10个在测绘集上的预测结果 直接取平均
        del pred

        del train_dataset, valid_dataset, test_dataset
        del train_loader, valid_loader, test_loader
        del train_x_tensor, train_y_tensor, valid_x_tensor, valid_y_tensor, test_x_tensor, test_y_tensor
        del model
        del criterion, optimizer, scheduler
        torch.cuda.empty_cache()
        gc.collect()

    oof_pred = np.argmax(meta_train, axis=1)  # 得到在完整训练集上的预测标签
    oof_f1_macro = f1_score(train_label, oof_pred, average='macro')  # 计算macro f1-score
    # 保存在完整训练集上的预测结果
    meta_train_path = f'../../oof_pred/{model_name}/{seed}/{model_name}_train_{oof_f1_macro:.4f}'
    if not os.path.exists(os.path.dirname(meta_train_path)):
        os.makedirs(os.path.dirname(meta_train_path))
    np.save(meta_train_path, meta_train)
    # 保存在测试集上的预测结果
    meta_test_path = f'../../oof_pred/{model_name}/{seed}/{model_name}_test_{oof_f1_macro:.4f}'
    if not os.path.exists(os.path.dirname(meta_test_path)):
        os.makedirs(os.path.dirname(meta_test_path))
    np.save(meta_test_path, meta_test)
