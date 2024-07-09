from TrainingDataProcessor import TrainingDataProcessor
from resenet50 import ResNet50_multi_label, preprocess_spectrograms_for_resnet50
from sklearn.model_selection import train_test_split
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.losses import BinaryCrossentropy
from tensorflow.keras.callbacks import EarlyStopping

if __name__ == '__main__':
    processor = TrainingDataProcessor()
    X, Y = processor.get_annotations()
    spectrograms_preprocessed = preprocess_spectrograms_for_resnet50(X)
    X_train, X_test, Y_train, Y_test = train_test_split(spectrograms_preprocessed, Y, test_size=0.2, random_state=42)
    model = ResNet50_multi_label(pretrained=True)
    model.compile(optimizer=Adam(learning_rate=0.0001), loss=BinaryCrossentropy(), metrics=['accuracy'])

    early_stopping = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)

    history = model.fit(
        X_train,
        Y_train,
        epochs=50,
        batch_size=32,
        validation_split=0.2,
        callbacks=[early_stopping]
    )

    loss, accuracy = model.evaluate(X_test, Y_test)
    print(f'Loss: {loss}, Accuracy: {accuracy}')
