export function FormContainer({ children, onSubmit }) {
    return (
        <form onSubmit={onSubmit} className='flex mx-auto flex-wrap -mx-3 bg-white rounded-lg shadow-lg p-2 md:p-8'>
            {children}
        </form>
    );
}