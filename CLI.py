from main import BooleanRetrievalModel


def main():
    # Initialize model
    ir_model = BooleanRetrievalModel()

    print("\nBoolean IR Model. Type 'exit' to quit.")
    print("-----------------------------------------------")

    while True:
        query = input("\nEnter your query: ").strip()
        if query.lower() == 'exit':
            print("Exiting. Goodbye!")
            break

        if not query:
            print("Please enter a valid query.")
            continue

        # Determine query type
        if '/' in query:
            results = ir_model.process_proximity_query(query)
        else:
            results = ir_model.process_boolean_query(query)

        if results:
            print("\nMatching Document IDs:")
            for i, doc_id in enumerate(results, start=1):
                print(f"{doc_id:<5}", end='')
                if i % 10 == 0:
                    print()
            print()
        else:
            print("\nNo matching documents found.")


if __name__ == '__main__':
    main()
